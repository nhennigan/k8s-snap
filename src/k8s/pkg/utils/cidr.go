package utils

import (
	"fmt"
	"math/big"
	"net"
	"regexp"
	"strconv"
	"strings"

	"github.com/canonical/lxd/lxd/util"
)

// findMatchingNodeAddress returns the IP address of a network interface that belongs to the given CIDR.
// It prefers the address with the fewest subnet bits.
// Loopback addresses are ignored.
func findMatchingNodeAddress(cidr *net.IPNet) (net.IP, error) {
	addrs, err := net.InterfaceAddrs()
	if err != nil {
		return nil, fmt.Errorf("could not get interface addresses: %w", err)
	}

	var selectedIP net.IP
	selectedSubnetBits := -1

	for _, addr := range addrs {
		ipNet, ok := addr.(*net.IPNet)
		if !ok {
			continue
		}
		if cidr.Contains(ipNet.IP) && !ipNet.IP.IsLoopback() {
			_, subnetBits := cidr.Mask.Size()
			if selectedSubnetBits == -1 || subnetBits < selectedSubnetBits {
				// Prefer the address with the fewest subnet bits
				selectedIP = ipNet.IP
				selectedSubnetBits = subnetBits
			}
		}
	}

	if selectedIP == nil {
		return nil, fmt.Errorf("could not find a matching address for CIDR %q", cidr.String())
	}

	return selectedIP, nil
}

// GetFirstIP returns the first IP address of a subnet. Use big.Int so that it can handle both IPv4 and IPv6 addreses.
func GetFirstIP(subnet string) (net.IP, error) {
	_, cidr, err := net.ParseCIDR(subnet)
	if err != nil {
		return nil, fmt.Errorf("%q is not a valid subnet CIDR: %w", subnet, err)
	}
	r := big.NewInt(0).Add(
		big.NewInt(0).SetBytes(cidr.IP.To16()),
		big.NewInt(1),
	).Bytes()
	r = append(make([]byte, 16), r...)
	return net.IP(r[len(r)-16:]), nil
}

// GetKubernetesServiceIPsFromServiceCIDRs returns a list of the first IP addrs from a given service cidr string.
func GetKubernetesServiceIPsFromServiceCIDRs(serviceCIDR string) ([]net.IP, error) {
	var firstIPs []net.IP
	cidrs := strings.Split(serviceCIDR, ",")
	if v := len(cidrs); v != 1 && v != 2 {
		return nil, fmt.Errorf("invalid ServiceCIDR value: %v", cidrs)
	}
	for _, cidr := range cidrs {
		ip, err := GetFirstIP(cidr)
		if err != nil {
			return nil, fmt.Errorf("could not get IP from CIDR %q: %w", cidr, err)
		}
		firstIPs = append(firstIPs, ip)
	}
	return firstIPs, nil
}

// ParseAddressString parses an address string and returns a canonical network address.
func ParseAddressString(address string, port int64) (string, error) {
	// Matches a CIDR block at the beginning of the address string
	// e.g. [2001:db8::/32]:8080
	re := regexp.MustCompile(`^\[?([a-z0-9:.]+\/[0-9]+)\]?`)
	cidrMatches := re.FindStringSubmatch(address)
	if len(cidrMatches) != 0 {
		// Resolve CIDR
		if _, ipNet, err := net.ParseCIDR(cidrMatches[1]); err == nil {
			matchingIP, err := findMatchingNodeAddress(ipNet)
			if err != nil {
				return "", fmt.Errorf("failed to find a matching node address for %q: %w", address, err)
			}
			address = strings.ReplaceAll(address, cidrMatches[1], matchingIP.String())
		}
	}

	host, hostPort, err := net.SplitHostPort(address)
	if err == nil {
		address = host
		port, err = strconv.ParseInt(hostPort, 10, 64)
		if err != nil {
			return "", fmt.Errorf("failed to parse the port from %q: %w", hostPort, err)
		}
	}

	if port < 0 || port > 65535 {
		return "", fmt.Errorf("invalid port number %d", port)
	}

	if address == "" {
		address = util.NetworkInterfaceAddress()
	}

	return net.JoinHostPort(address, fmt.Sprintf("%d", port)), nil
}

// GetDefaultAddress returns the default IPv4 and IPv6 addresses of the host.
func GetDefaultAddress() (ipv4, ipv6 string, err error) {
	// Get a list of network interfaces.
	interfaces, err := net.Interfaces()
	if err != nil {
		return "", "", fmt.Errorf("failed to get network interfaces: %w", err)
	}

	// Loop through each network interface
	for _, iface := range interfaces {
		// Skip interfaces that are down or loopback interfaces
		if iface.Flags&net.FlagUp == 0 || iface.Flags&net.FlagLoopback != 0 {
			continue
		}

		// Get a list of addresses for the current interface.
		addrs, err := iface.Addrs()
		if err != nil {
			return "", "", fmt.Errorf("failed to get addresses for interface %q: %w", iface.Name, err)
		}

		// Loop through each address
		for _, addr := range addrs {
			// Parse the address to get the IP
			var ip net.IP
			switch v := addr.(type) {
			case *net.IPNet:
				ip = v.IP
			case *net.IPAddr:
				ip = v.IP
			}

			// Check if it's an IPv4 or IPv6 address and not a loopback
			if ip.IsLoopback() {
				continue
			}

			if ip.To4() != nil && ipv4 == "" {
				ipv4 = ip.String()
			} else if ip.To4() == nil && ipv6 == "" {
				ipv6 = ip.String()
			}

			// Break early if both IPv4 and IPv6 addresses are found
			if ipv4 != "" && ipv6 != "" {
				return ipv4, ipv6, nil
			}
		}
	}

	return ipv4, ipv6, nil
}

// FindCIDRForIP returns the CIDR block that contains the given IP address.
func FindCIDRForIP(nodeIp net.IP) (cidr string, err error) {
	// Get a list of network interfaces.
	interfaces, err := net.Interfaces()
	if err != nil {
		return "", fmt.Errorf("failed to get network interfaces: %w", err)
	}

	// Loop through each network interface
	for _, iface := range interfaces {
		// Skip interfaces that are down
		if iface.Flags&net.FlagUp == 0 {
			continue
		}

		// Get a list of addresses for the current interface.
		addrs, err := iface.Addrs()
		if err != nil {
			return "", fmt.Errorf("failed to get addresses for interface %q: %w", iface.Name, err)
		}

		// Loop through each address
		for _, addr := range addrs {
			// Parse the address to get the IP
			var ipNet *net.IPNet

			switch v := addr.(type) {
			case *net.IPNet:
				ipNet = v
			default:
				continue
			}

			if ipNet.Contains(nodeIp) {
				return ipNet.String(), nil
			}
		}
	}

	return "", fmt.Errorf("no CIDR found for IP %q", nodeIp.String())
}

// SplitCIDRStrings parses the given CIDR string and returns the respective IPv4 and IPv6 CIDRs.
func SplitCIDRStrings(cidrString string) (string, string, error) {
	clusterCIDRs := strings.Split(cidrString, ",")
	if v := len(clusterCIDRs); v != 1 && v != 2 {
		return "", "", fmt.Errorf("invalid CIDR list: %v", clusterCIDRs)
	}

	var (
		ipv4CIDR string
		ipv6CIDR string
	)
	for _, cidr := range clusterCIDRs {
		_, parsed, err := net.ParseCIDR(cidr)
		switch {
		case err != nil:
			return "", "", fmt.Errorf("failed to parse cidr: %w", err)
		case parsed.IP.To4() != nil:
			ipv4CIDR = cidr
		default:
			ipv6CIDR = cidr
		}
	}
	return ipv4CIDR, ipv6CIDR, nil
}

// IsIPv4 returns true if the address is a valid IPv4 address, false otherwise.
// The address may contain a port number.
func IsIPv4(address string) bool {
	ip := strings.Split(address, ":")[0]
	parsedIP := net.ParseIP(ip)
	return parsedIP != nil && parsedIP.To4() != nil
}

// ToIPString returns the string representation of an IP address.
// If the IP address is an IPv6 address, it is enclosed in square brackets.
func ToIPString(ip net.IP) string {
	if ip.To4() != nil {
		return ip.String()
	}
	return "[" + ip.String() + "]"
}

// CIDRsOverlap checks if two given CIDR blocks overlap.
// It takes two strings representing the CIDR blocks as input and returns a boolean indicating
// whether they overlap and an error if any of the CIDR blocks are invalid.
func CIDRsOverlap(cidr1, cidr2 string) (bool, error) {
	_, ipNet1, err1 := net.ParseCIDR(cidr1)
	_, ipNet2, err2 := net.ParseCIDR(cidr2)

	if err1 != nil {
		return false, fmt.Errorf("couldn't parse CIDR block %q: %w", cidr1, err1)
	}

	if err2 != nil {
		return false, fmt.Errorf("couldn't parse CIDR block %q: %w", cidr2, err2)
	}

	if ipNet1.Contains(ipNet2.IP) || ipNet2.Contains(ipNet1.IP) {
		return true, nil
	}

	return false, nil
}

// JoinHostPort is like net.JoinHostPort but accepts an int for the port number.
func JoinHostPort(host string, port int) string {
	return net.JoinHostPort(host, strconv.Itoa(port))
}

package setup

import (
	"fmt"

	"github.com/canonical/k8s/pkg/utils/cert"
)

// InitCertificates sets up the CAs and the necessary server certificates that is used by Kubernetes.
// An initial CertificateAuthority can be provided. If not, a self-signed one will be generated.
func InitCertificates(ca *cert.CertKeyPair) (*cert.CertificateManager, error) {
	certMan, err := cert.NewCertificateManager()
	if err != nil {
		return nil, fmt.Errorf("failed to create certificate manager: %w", err)
	}

	if ca != nil {
		certMan.CA = ca
	} else {
		err = certMan.GenerateCA()
		if err != nil {
			return nil, fmt.Errorf("failed to generate certificate authority: %w", err)
		}
	}

	err = certMan.GenerateFrontProxyCA()
	if err != nil {
		return nil, fmt.Errorf("failed to generate front proxy certificate authority: %w", err)
	}

	err = certMan.GenerateServerCerts()
	if err != nil {
		return nil, fmt.Errorf("failed to generate server certificates: %w", err)
	}

	err = certMan.GenerateServiceAccountKey()
	if err != nil {
		return nil, fmt.Errorf("failed to generate service account key: %w", err)
	}

	return certMan, nil
}

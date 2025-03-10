package contour

import (
	"embed"

	"github.com/canonical/k8s/pkg/client/helm"
)

//go:embed all:charts
var ChartFS embed.FS

var (
	// chartContour represents manifests to deploy Contour.
	// This excludes shared CRDs.
	chartContour = helm.InstallableChart{
		Name:             "contour",
		Version:          "17.0.4",
		InstallName:      "ck-ingress",
		InstallNamespace: "projectcontour",
	}
	// chartGateway represents manifests to deploy Contour Gateway.
	// This excludes shared CRDs.
	chartGateway = helm.InstallableChart{
		Name:             "ck-gateway-contour",
		Version:          "1.28.2",
		InstallName:      "ck-gateway",
		InstallNamespace: "projectcontour",
	}
	// chartDefaultTLS represents manifests to deploy a delegation resource for the default TLS secret.
	chartDefaultTLS = helm.InstallableChart{
		Name:             "ck-ingress-tls",
		Version:          "0.1.0",
		InstallName:      "ck-ingress-tls",
		InstallNamespace: "projectcontour-root",
	}
	// chartCommonContourCRDS represents manifests to deploy common Contour CRDs.
	chartCommonContourCRDS = helm.InstallableChart{
		Name:             "ck-contour-common",
		Version:          "1.28.2",
		InstallName:      "ck-contour-common",
		InstallNamespace: "projectcontour",
	}

	// ContourGatewayProvisionerEnvoyImageRepo represents the image to use for envoy in the gateway.
	ContourGatewayProvisionerEnvoyImageRepo = "ghcr.io/canonical/k8s-snap/envoyproxy/envoy"

	// NOTE: The image version is v1.29.2 instead of 1.28.2
	// to follow the upstream configuration for the contour gateway provisioner.
	// ContourGatewayProvisionerEnvoyImageTag is the tag to use for envoy in the gateway.
	ContourGatewayProvisionerEnvoyImageTag = "v1.29.2"

	// ContourIngressEnvoyImageRepo represents the image to use for the Contour Envoy proxy.
	ContourIngressEnvoyImageRepo = "ghcr.io/canonical/k8s-snap/bitnami/envoy"

	// ContourIngressEnvoyImageTag is the tag to use for the Contour Envoy proxy image.
	ContourIngressEnvoyImageTag = "1.28.2-debian-12-r0"

	// ContourIngressContourImageRepo represents the image to use for Contour.
	ContourIngressContourImageRepo = "ghcr.io/canonical/k8s-snap/bitnami/contour"

	// ContourIngressContourImageTag is the tag to use for the Contour image.
	ContourIngressContourImageTag = "1.28.2-debian-12-r4"

	// ContourGatewayProvisionerContourImageRepo represents the image to use for the Contour Gateway Provisioner.
	ContourGatewayProvisionerContourImageRepo = "ghcr.io/canonical/k8s-snap/projectcontour/contour"

	// ContourGatewayProvisionerContourImageTag is the tag to use for the Contour Gateway Provisioner image.
	ContourGatewayProvisionerContourImageTag = "v1.28.2"
)

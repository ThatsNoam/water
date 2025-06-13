#!/usr/bin/env python3
"""
SSL/TLS Utilities for Remote Control System
Provides secure communication infrastructure.
"""

import ssl
import socket
import os
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import ipaddress

class SSLManager:
    def __init__(self):
        self.cert_file = "server.crt"
        self.key_file = "server.key"
        self.ca_cert_file = "ca.crt"
        self.ca_key_file = "ca.key"
        
    def generate_ca_certificate(self):
        """Generate a Certificate Authority (CA) certificate."""
        # Generate private key for CA
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create CA certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IL"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Israel"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Tel Aviv"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Remote Control System"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Remote Control CA"),
        ])
        
        ca_cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            ca_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        ).add_extension(
            x509.KeyUsage(
                key_encipherment=True,
                digital_signature=True,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).sign(ca_key, hashes.SHA256())
        
        # Save CA certificate and key
        with open(self.ca_cert_file, "wb") as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
            
        with open(self.ca_key_file, "wb") as f:
            f.write(ca_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        return ca_cert, ca_key
        
    def generate_server_certificate(self, ca_cert=None, ca_key=None):
        """Generate a server certificate signed by the CA."""
        if not ca_cert or not ca_key:
            ca_cert, ca_key = self.load_ca_certificate()
            
        # Generate private key for server
        server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create server certificate
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IL"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Israel"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Tel Aviv"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Remote Control System"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Remote Control Server"),
        ])
        
        server_cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            server_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("*.local"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                x509.IPAddress(ipaddress.IPv4Address("0.0.0.0")),
            ]),
            critical=False,
        ).add_extension(
            x509.KeyUsage(
                key_encipherment=True,
                digital_signature=True,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                content_commitment=False,
                data_encipherment=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).sign(ca_key, hashes.SHA256())
        
        # Save server certificate and key
        try:
            with open(self.cert_file, "wb") as f:
                f.write(server_cert.public_bytes(serialization.Encoding.PEM))
                
            with open(self.key_file, "wb") as f:
                f.write(server_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            print(f"✅ Server certificate and key saved: {self.cert_file}, {self.key_file}")
        except Exception as e:
            print(f"❌ Error saving server certificate: {e}")
            raise
            
        return server_cert, server_key
        
    def load_ca_certificate(self):
        """Load existing CA certificate and key."""
        with open(self.ca_cert_file, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
            
        with open(self.ca_key_file, "rb") as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None)
            
        return ca_cert, ca_key
        
    def setup_certificates(self):
        """Setup all required certificates."""
        # Check if certificates exist
        if not os.path.exists(self.ca_cert_file) or not os.path.exists(self.ca_key_file):
            print("🔐 Generating CA certificate...")
            ca_cert, ca_key = self.generate_ca_certificate()
        else:
            ca_cert, ca_key = self.load_ca_certificate()
            
        if not os.path.exists(self.cert_file) or not os.path.exists(self.key_file):
            print("🔐 Generating server certificate...")
            self.generate_server_certificate(ca_cert, ca_key)
            
        print("✅ SSL certificates ready!")
        
    def create_server_context(self):
        """Create SSL context for server."""
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # For internal network use
        
        try:
            context.load_cert_chain(self.cert_file, self.key_file)
        except FileNotFoundError:
            print("⚠️ SSL certificates not found, generating new ones...")
            self.setup_certificates()
            context.load_cert_chain(self.cert_file, self.key_file)
            
        return context
        
    def create_client_context(self):
        """Create SSL context for client."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # For internal network use
        
        return context
        
    def wrap_server_socket(self, sock):
        """Wrap a server socket with SSL."""
        context = self.create_server_context()
        return context.wrap_socket(sock, server_side=True)
        
    def wrap_client_socket(self, sock, server_hostname="localhost"):
        """Wrap a client socket with SSL."""
        context = self.create_client_context()
        return context.wrap_socket(sock, server_hostname=server_hostname)

# Global SSL manager instance
ssl_manager = SSLManager()

def initialize_ssl():
    """Initialize SSL certificates and contexts."""
    try:
        ssl_manager.setup_certificates()
        return True
    except Exception as e:
        print(f"❌ Failed to initialize SSL: {e}")
        return False

def create_secure_server_socket(host, port):
    """Create a secure server socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    return ssl_manager.wrap_server_socket(sock)

def create_secure_client_socket():
    """Create a secure client socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return sock  # Will be wrapped when connecting

def connect_secure_client(sock, host, port):
    """Connect a client socket securely."""
    sock.connect((host, port))
    return ssl_manager.wrap_client_socket(sock, server_hostname=host) 
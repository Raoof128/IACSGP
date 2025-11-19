# Security Group Policies
# Prevents insecure security group configurations

package terraform.security_groups

import rego.v1

# Get all security group resources
security_groups := [sg |
    sg := input.resource_changes[_]
    sg.type == "aws_security_group"
]

# DENY: Security groups must not allow SSH (22) from 0.0.0.0/0
deny_ssh_from_internet[msg] {
    sg := security_groups[_]
    ingress := sg.change.after.ingress[_]

    # Check if port 22 is open
    ingress.from_port <= 22
    ingress.to_port >= 22

    # Check if open to the internet
    cidr := ingress.cidr_blocks[_]
    cidr == "0.0.0.0/0"

    msg := sprintf("Security group '%s' allows SSH (port 22) from 0.0.0.0/0 - this is a critical security risk", [sg.address])
}

# DENY: Security groups must not allow RDP (3389) from 0.0.0.0/0
deny_rdp_from_internet[msg] {
    sg := security_groups[_]
    ingress := sg.change.after.ingress[_]

    # Check if port 3389 is open
    ingress.from_port <= 3389
    ingress.to_port >= 3389

    # Check if open to the internet
    cidr := ingress.cidr_blocks[_]
    cidr == "0.0.0.0/0"

    msg := sprintf("Security group '%s' allows RDP (port 3389) from 0.0.0.0/0 - this is a critical security risk", [sg.address])
}

# DENY: Security groups must not allow all ports from 0.0.0.0/0
deny_all_ports_from_internet[msg] {
    sg := security_groups[_]
    ingress := sg.change.after.ingress[_]

    # Check if all ports are open (0 or very wide range)
    ingress.from_port == 0
    ingress.to_port >= 65535

    # Check if open to the internet
    cidr := ingress.cidr_blocks[_]
    cidr == "0.0.0.0/0"

    msg := sprintf("Security group '%s' allows ALL ports from 0.0.0.0/0 - this is a critical security risk", [sg.address])
}

# DENY: Security groups must not allow wide port ranges from internet
deny_wide_port_range_from_internet[msg] {
    sg := security_groups[_]
    ingress := sg.change.after.ingress[_]

    # Check for wide port range (more than 100 ports)
    port_range := ingress.to_port - ingress.from_port
    port_range > 100

    # Check if open to the internet
    cidr := ingress.cidr_blocks[_]
    cidr == "0.0.0.0/0"

    # Exclude common wide ranges that might be intentional
    not is_approved_wide_range(ingress.from_port, ingress.to_port)

    msg := sprintf("Security group '%s' allows wide port range (%d-%d) from 0.0.0.0/0", [sg.address, ingress.from_port, ingress.to_port])
}

# Helper function for approved wide ranges
is_approved_wide_range(from, to) {
    from == 443
    to == 443
}

# WARN: Security groups should have descriptions for all rules
warn_missing_rule_description[msg] {
    sg := security_groups[_]
    ingress := sg.change.after.ingress[_]

    not ingress.description

    msg := sprintf("Security group '%s' has ingress rule without description", [sg.address])
}

warn_missing_rule_description[msg] {
    sg := security_groups[_]
    ingress := sg.change.after.ingress[_]

    ingress.description == ""

    msg := sprintf("Security group '%s' has ingress rule with empty description", [sg.address])
}

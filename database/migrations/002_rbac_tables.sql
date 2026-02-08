-- RBAC Tables Migration
-- Version: 002
-- Description: Role-Based Access Control tables

-- Roles table
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT false, -- System roles cannot be deleted
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Permissions table
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    resource VARCHAR(100) NOT NULL, -- e.g., 'scans', 'projects', 'users'
    action VARCHAR(50) NOT NULL, -- e.g., 'create', 'read', 'update', 'delete'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Role-Permission mapping
CREATE TABLE role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- User-Role mapping
CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID REFERENCES users(id),
    PRIMARY KEY (user_id, role_id, organization_id)
);

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX idx_user_roles_org_id ON user_roles(organization_id);

-- Insert default roles
INSERT INTO roles (name, display_name, description, is_system) VALUES
    ('admin', 'Administrator', 'Full system access', true),
    ('team_lead', 'Team Lead', 'Manage team and projects', true),
    ('developer', 'Developer', 'Run scans and view results', true),
    ('scanner', 'Scanner', 'Read-only scan execution', true),
    ('viewer', 'Viewer', 'Read-only access', true);

-- Insert default permissions
INSERT INTO permissions (name, display_name, description, resource, action) VALUES
    -- Scan permissions
    ('scans.create', 'Create Scans', 'Create new security scans', 'scans', 'create'),
    ('scans.read', 'View Scans', 'View scan results', 'scans', 'read'),
    ('scans.update', 'Update Scans', 'Update scan configuration', 'scans', 'update'),
    ('scans.delete', 'Delete Scans', 'Delete scans', 'scans', 'delete'),
    
    -- Project permissions
    ('projects.create', 'Create Projects', 'Create new projects', 'projects', 'create'),
    ('projects.read', 'View Projects', 'View projects', 'projects', 'read'),
    ('projects.update', 'Update Projects', 'Update project settings', 'projects', 'update'),
    ('projects.delete', 'Delete Projects', 'Delete projects', 'projects', 'delete'),
    
    -- User permissions
    ('users.create', 'Create Users', 'Create new users', 'users', 'create'),
    ('users.read', 'View Users', 'View user list', 'users', 'read'),
    ('users.update', 'Update Users', 'Update user details', 'users', 'update'),
    ('users.delete', 'Delete Users', 'Delete users', 'users', 'delete'),
    
    -- Organization permissions
    ('organizations.read', 'View Organization', 'View organization details', 'organizations', 'read'),
    ('organizations.update', 'Update Organization', 'Update organization settings', 'organizations', 'update'),
    
    -- Report permissions
    ('reports.generate', 'Generate Reports', 'Generate security reports', 'reports', 'create'),
    ('reports.export', 'Export Reports', 'Export reports to PDF/CSV', 'reports', 'export'),
    
    -- Settings permissions
    ('settings.read', 'View Settings', 'View system settings', 'settings', 'read'),
    ('settings.update', 'Update Settings', 'Update system settings', 'settings', 'update');

-- Assign permissions to roles

-- Admin: All permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r CROSS JOIN permissions p
WHERE r.name = 'admin';

-- Team Lead: Most permissions except user/org management
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r CROSS JOIN permissions p
WHERE r.name = 'team_lead'
AND p.name IN (
    'scans.create', 'scans.read', 'scans.update', 'scans.delete',
    'projects.create', 'projects.read', 'projects.update', 'projects.delete',
    'users.read',
    'organizations.read',
    'reports.generate', 'reports.export',
    'settings.read'
);

-- Developer: Can create scans and view results
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r CROSS JOIN permissions p
WHERE r.name = 'developer'
AND p.name IN (
    'scans.create', 'scans.read', 'scans.update',
    'projects.read',
    'reports.generate', 'reports.export'
);

-- Scanner: Can only execute scans
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r CROSS JOIN permissions p
WHERE r.name = 'scanner'
AND p.name IN (
    'scans.create', 'scans.read',
    'projects.read'
);

-- Viewer: Read-only
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r CROSS JOIN permissions p
WHERE r.name = 'viewer'
AND p.name IN (
    'scans.read',
    'projects.read',
    'reports.generate'
);

-- Assign admin role to default admin user
INSERT INTO user_roles (user_id, role_id, organization_id)
SELECT u.id, r.id, NULL
FROM users u, roles r
WHERE u.username = 'admin' AND r.name = 'admin';

-- Add trigger for roles
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

export function normalizeRoleValue(rawRole) {
  const value =
    typeof rawRole === "object" && rawRole !== null
      ? rawRole.roleName || rawRole.name || rawRole.role || rawRole.value
      : rawRole;

  const normalized = String(value || "")
    .replace(/^ROLE_/i, "")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toUpperCase();

  const compact = normalized.replace(/\s+/g, "");
  const aliasMap = {
    SUPERADMIN: "SUPER ADMIN",
    ADMIN: "ADMIN STORE",
    STACKSTAFF: "STACK STAFF",
    TECHNICALSTAFF: "TECHNICAL STAFF",
    MEMBER: "MEMBER",
    FRONTDESKSTAFF: "FRONT DESK STAFF",
  };

  return aliasMap[compact] || normalized;
}

export function getUserRoleLabel(user) {
  if (!user) return "";
  return normalizeRoleValue(user.roleName || user.role || user.userRole);
}

export function getDefaultLandingPath(user) {
  return "/app/dashboard";
}

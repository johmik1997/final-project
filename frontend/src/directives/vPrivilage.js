import { useAuth } from "@/stores/auth";

function checkPrivilage(el, { value, modifiers }) {
  if (!value && !modifiers) return;

  const authStore = useAuth();
  let user = authStore.auth?.user;

  if (!user) {
    let storedUser = localStorage.getItem("userDetail");
    if (storedUser) {
      user = JSON.parse(storedUser);
    }
  }

  if (user?.privileges.includes("All Privileges") || user.roleName === 'Super Admin') return;

  if (modifiers?.role && value) {
    if (user.roleName !== value) {
      el.remove();
    }
    return;
  }

  if (value instanceof Array) {
    let privileges = user?.privileges;

    const found = value?.find((privilage) => {
      return privileges?.includes(`ROLE_${privilage}`);
    });

    if (!found) {
      el.remove();
    }
  }
}

const vPrivilage = {
  mounted: checkPrivilage,
  updated: checkPrivilage,
};

export default vPrivilage;

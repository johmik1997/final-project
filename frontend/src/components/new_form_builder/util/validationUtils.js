function validationKeys(validation) {
  const rules = new String(validation);

  return rules.split("|").reduce((state, rule) => {
    const [name, args] = rule.split("-");

    if (!args) {
      state[name] = {
        args: true,
        message: null,
      };

      return state;
    }

    const [params, ...messages] = args.split(" ");

    if ((params && params.includes(",")) || (params && !params.includes("("))) {
      const arg = params?.split(",") || true;
      const message = messages.join(" ").replace(/[()]/g, "");

      state[name] =
        arg?.length == 1
          ? {
              args: arg[0],
              message,
            }
          : {
              args: arg,
              message,
            };
    } else if (params && params.includes("(")) {
      const message = [params, ...messages].join(" ").replace(/[()]/g, "");
      state[name] = {
        args: null,
        message,
      };
    } else {
      state[name] = {
        args: true,
        message: null,
      };
    }

    return state;
  }, {});
}

export { validationKeys };

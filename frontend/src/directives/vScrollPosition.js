export default {
  created: (el, { value, modifiers }) => {
    try {
      if (typeof value != "function") {
        throw new Error("[v-scroll-position]'s [value] must be a function");
      }

      let pos = Object.keys(modifiers)?.[0]
      pos = pos ? parseInt(pos) : 0
      el.addEventListener("scroll", (ev) => {
        value(ev.target.scrollTop, pos);
      });
    } catch (err) {
      console.error(err);
    }
  },
};

function array_length(value, args, formId, message) {  
  console.log(value, args, message);
  
  if(value.length == 0) return [false, args?.message ?? 'Add At Least One']
  return [true]
}

function calculateAge(dateOfBirth) {
  const today = new Date();
  const birthDate = new Date(dateOfBirth);
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();

  if (
    monthDiff < 0 ||
    (monthDiff === 0 && today.getDate() < birthDate.getDate())
  ) {
    age--;
  }

  return age;
}

function required(value, _, __, message) {
  if (value) return [true];

  return [false, message || `This field is required`];
}

function requiredFile(value, _, __, message) {
  if (value instanceof FileList) {
    if (value.length) return [true];

    return [false, message || `This field is required`];
  }
  return required(value);
}

function fileSize(file, maxSize, __, message) {
  let size = maxSize.match(/\d+/g)?.[0] || 0;
  let unit = maxSize.match(/[^0-9]\w/g)?.[0];

  let msg = message || "image must be less than or equal to";

  function checkKBSize() {
    if (file.size / 1000 <= size) return [true];

    return [false, `${msg} ${maxSize}`];
  }

  function checkMBSize() {
    if (file.size / 1000 / 1000 <= size) return [true];

    return [false, `${msg} ${maxSize}`];
  }

  switch (unit) {
    case "kb":
      return checkKBSize();
    case "mb":
      return checkMBSize();
    default:
      return [false, "not a valid unit"];
  }
}

function max(value, maxValue = 0, _, message) {
  if (value.length < parseInt(maxValue.args)) return [true];

  return [false, message || `must be less than ${maxValue.args}`];
}

function maxnum(value, maxValue = 0, _, message) {
  if (value < maxValue) return [true];

  return [false, message || `must be less than ${maxValue}`];
}

function exactly(value, maxValue = 0, _, message) {
  if (value == maxValue) return [true];

  return [false, message || `must be exactly ${maxValue}`];
}

function minmax(value, minMaxValue, _, message) {
  if (value.length >= minMaxValue[0] && value.length < minMaxValue[1])
    return [true];

  return [
    false,
    message ||
      `must be greater than ${minMaxValue[0]} and less than ${minMaxValue[1]}`,
  ];
}

function min(value, minValue = 0, _, message) {
  if (value.length >= minValue) return [true];

  return [false, message || `must be greater than ${minValue}`];
}

function email(value, _, __, message) {
  if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(value))
    return [true];

  return [false, message || `not a valid email`];
}

// let emailAbortController
// async function emailExists(email) {
// 	if(emailAbortController) emailAbortController.abort()

// 	emailAbortController = new AbortController()

// 	try {
// 		const response = await axios.get(`${URL}users/exists/email/${email}`, {
// 			signal: emailAbortController.signal
// 		})

// 		if(!response) return [true]

// 		return [false, `email already exists`]

// 	} catch (err) {
// 		if(err?.response?.status == 404) {
// 			return [true]
// 		}
// 		return [false, '']
// 	}
// }

// let shopAbortController
// async function shopExists(shop) {
// 	if(shopAbortController) shopAbortController.abort()

// 	shopAbortController = new AbortController()

// 	try {
// 		const response = await axios.get(`${URL}shops/exists/${shop}`, {
// 			signal: shopAbortController.signal
// 		})

// 		if(!response) return [true]

// 		return [false, `shop already exists`]

// 	} catch (err) {
// 		if(err?.response?.status == 404) {
// 			return [true]
// 		}
// 		return [false, '']
// 	}
// }

// let telegramAbortController
// async function telegramExists(telegram) {
// 	if(telegramAbortController) telegramAbortController.abort()

// 	telegramAbortController = new AbortController()

// 	try {
// 		const response = await axios.get(`${URL}shops/exists/telegram${telegram}`, {
// 			signal: telegramAbortController.signal
// 		})

// 		if(!response) return [true]

// 		return [false, `telegram already exists`]

// 	} catch (err) {
// 		if(err?.response?.status == 404) {
// 			return [true]
// 		}
// 		return [false, '']
// 	}
// }

// let phoneAbortController
// async function phoneExists(phone) {
// 	if(phoneAbortController) phoneAbortController.abort()

// 	phoneAbortController = new AbortController()

// 	try {
// 		const response = await axios.get(`${URL}users/exists/phone/${phone}`, {
// 			signal: phoneAbortController.signal
// 		})

// 		if(!response) return [true]

// 		return [false, `phone already exists`]
// 	} catch (err) {
// 		if(err?.response?.status == 404) return [true]

// 		return [false, '']
// 	}
// }

function num(value, limit, _, message) {
  let regex = /^[0-9]+$/;
  if (limit instanceof Array) {
    if (limit.length == 1) regex = new RegExp(`^[0-9]{${limit[0]}}$`);
    if (limit.length > 1)
      regex = new RegExp(`^[0-9]{${limit[0]},${limit[1] + 1}}$`);
  }

  if (regex.test((value))) return [true];

  return [false, message || `not a valid number`];
}

function num_minmax(value, limit, _, message) {
  if (value >= limit[0] && value <= limit[1]) return [true];

  return [false, message || `must be between ${limit}`];
}

function phone(value, limit, _, message) {
  let regex = /^(\+?2519|09)[0-9]{8}$/;
  if (regex.test(value)) return [true];

  return [false, message || `not a valid phone number`];
}

function alpha(value, limit, _, message) {
  let regex = /^[ a-zA-Z]+$/;

  if (limit instanceof Array) {
    if (limit.length === 1) regex = new RegExp(`^[ a-zA-Z]{${limit[0]},}$`); // Min limit only
    if (limit.length > 1) regex = new RegExp(`^[ a-zA-Z]{${limit[0]},${limit[1]}}$`); // Min & Max limit
  }

  if (!regex.test(value)) {
    return [false, message || `Not a valid alphabet`];
  }

  if (value.length <= 2) {
    return [false, message || `Input must be more than 2 letters`];
  }

  return [true];
}


function equalTo(value, name, formid, message) {
  let form = document.querySelector("#" + formid);
  if (form[name.args].value == value) return [true];

  return [false, message || `does'nt much the password`];
}

function exact(value, val, _, message) {
  if (value == val) return [true];

  return [false, message || `does'nt much the password`];
}

function num_min(input, limit, _, message) {
  if (parseInt(input) >= limit) return [true];

  return [false, message || `must be greater than or equal to ${limit}`];
}

function num_max(input, limit, _, message) {

  if (parseFloat(`${input}`) <= limit) return [true];

  return [false, message || `The required amount is not available`];
}

function balance_check(input, limit, _, message) {
  if (parseFloat(input) <= limit) return [true];

  return [false, message || `balance only sufficeient for only ${limit}`];
}

function len(value, minValue = 0, _, message) {
  if (value.length == minValue) return [true];

  return [false, message || `the length must be ${minValue}`];
}

function olderThan(value, age, _, message) {
  const givenAge = calculateAge(value);
  if (givenAge >= age) return [true];
  return [false, `must be older that ${age}`];
}

function oneof(value, values = [], _, message) {
  return values.includes(value)
    ? [true]
    : [false, message || `must be USED or NEW`];
}

function isTrue(value, val = false, _, message) {
  return val == value ? [true] : [false, message || "this need to be true"];
}

function greaterThanToday(value) {
  var date = new Date(value);
  var now = new Date();
  if (date > now) return [true];
  return [false, "Must be latter that today"];
}

function addBeneficiaries(value, values = [], _, message) {
  if (
    (value || []).length == 1 &&
    value.every((el) => {
      return Object.keys(el).every((key) => {
        if (key == "id") return true;
        return !!el[key] == false;
      });
    })
  )
    return [true];

  const sum = (value || []).reduce((sum, el) => (sum += parseInt(el.share)), 0);
  if (sum > 100) {
    return [false, "the sume of all the Shares need to add up to 100%"];
  }

  if (
    value.every((el) => {
      return Object.values(el).every((el) => !!el == true);
    })
  ) {
    return [true];
  } else {
    return [false, "fill all the beneficiary fields"];
  }
}

function date_thisYear(value) {}

function requiredMultipleSelect(value, _, __, message) {
  function check(ary) {
    if (!(ary instanceof Array) || ary.length == 0)
      return [false, message || "This field is required"];

    return [true];
  }
  if (value && value.includes(",")) {
    return check(value.split(","));
  }
  return check(value);
}
const added = {};

const common = {
  array_length,
  alpha,
  max,
  min,
  num,
  numeric: num,
  len,
  exact,
  required,
  equalTo,
  maxnum,
  minmax,
  exactly,
  greaterThanToday,
  addBeneficiaries,
  date_thisYear,
  num_min,
  num_max,
  balance_check,
  requiredMultipleSelect,
  num_minmax
  // shopExists,
  // telegramExists,
  // phoneExists,
  // emailExists,
};

const checkbox = {
  required,
};

const select = {
  required,
};

const file = {
  required: requiredFile,
  fileSize,
};

const textarea = common;
const text = {
  ...common,
  email(value, _, __, message) {
    if (!value) return [false, message || "Email is required"];
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(value)) {
      return [true];
    }
    return [false, message || "Please enter a valid email address"];
  },
  phone,
  oneof,
};

const date = { ...common, olderThan };

const password = text;

Object.setPrototypeOf(checkbox, added);
Object.setPrototypeOf(select, added);
Object.setPrototypeOf(file, added);
Object.setPrototypeOf(textarea, added);
Object.setPrototypeOf(text, added);
Object.setPrototypeOf(password, added);

export function addValidator(validators) {
  if (validators instanceof Array) {
    validators.map((validator) => {
      added[validator.name] = validator;
    });
  } else {
    added[validators.name] = validators;
  }
}

function pass(value, limit, _, message) {
  // Password validation: at least 6 characters with numbers or letters
  const minLength = limit || 6;
  
  if (!value || value.length < minLength) {
    return [false, message || `Password must be at least ${minLength} characters long`];
  }
  
  // Must contain at least letters or numbers
  if (!/[a-zA-Z0-9]/.test(value)) {
    return [false, message || `Password must contain letters or numbers`];
  }
  
  return [true];
}

export function getValidators() {
  return {
    checkbox,
    select,
    file,
    textarea,
    text: {
      ...common,
      email(value, _, __, message) {
        if (!value) return [false, message || "Email is required"];
        if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(value)) {
          return [true];
        }
        return [false, message || "Please enter a valid email address"];
      },
      phone,
      oneof,
      pass, // Add pass validator to text
    },
    password: {
      required,
      pass, // Add pass validator to password
    },
    date,
  };
}

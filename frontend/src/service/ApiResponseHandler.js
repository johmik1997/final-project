export async function responseHandler(request) {
  if (!(request instanceof Promise)) return;

  return request
    .then((res) => {
      return {
        status: res.status,
        data: res.data,
        success: true,
        error: "",
      };
    })
    .catch((error) => {
      const getErrorMessage = (data) => {
        if (!data) return "";
        if (typeof data === "string") return data;
        if (data?.message) return data.message;
        if (data?.detail) return data.detail;
        if (Array.isArray(data)) return data.filter(Boolean).join(" ");

        return Object.entries(data)
          .map(([key, value]) => {
            if (Array.isArray(value)) return `${key === "non_field_errors" ? "" : `${key}: `}${value.filter(Boolean).join(", ")}`.trim();
            if (typeof value === "object") return `${key}: ${getErrorMessage(value)}`;
            if (value != null) return `${key}: ${String(value)}`;
            return "";
          })
          .filter(Boolean)
          .join(" | ");
      };

      // this is true when the request gets to the server
      // and there is some error on the server
      if (error.response) {
        return {
          success: false,
          data: null,
          status: error.response.status,
          error: getErrorMessage(error.response.data) || error.message,
        };
      }
      // this is true when the request cant get to the server
      // eg. connection error
      if (error.request) {
        return {
          success: false,
          data: null,
          status: error.code,
          error: error.message,
        };
      }
    });
}

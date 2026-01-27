"use client";

export default function Input({
  label,
  type = "text",
  placeholder,
  value,
  onChange,
  name,
  rows = 4,
  ...props
}) {
  const base =
    "outline-none transition-all duration-200 w-0 lg:w-full sm:w-20 md:w-50 placeholder-gray-500 ";

  const inputStyles = {
    text:
      "px-3 py-2 rounded-md border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
    email:
      "px-3 py-2 rounded-md border border-green-400 bg-green-50 focus:ring-2 focus:ring-green-200",
    password:
      "px-3 py-2 rounded-md border border-purple-400 bg-purple-50 tracking-wider focus:ring-2 focus:ring-purple-200",
    search:
      "pl-10 pr-3 py-2 rounded-full bg-gray-600 border border-gray-300 focus:ring-2 focus:ring-gray-200",
    number:
      "px-3 py-2 rounded-md border-2 border-dashed border-orange-400 bg-orange-50 focus:ring-2 focus:ring-orange-200",
    date:
      "px-3 py-2 rounded-md border border-indigo-400 bg-indigo-50 text-indigo-700 focus:ring-2 focus:ring-indigo-200",
    file:
      "px-3 py-2 rounded-md border border-slate-400 bg-slate-100 file:mr-4 file:px-4 file:py-2 file:rounded file:border-0 file:bg-slate-700 file:text-white hover:file:bg-slate-800",
    textarea:
      "px-3 py-2 rounded-lg border border-teal-400 bg-teal-50 resize-none focus:ring-2 focus:ring-teal-200",
  };

  const defaultplaceholder = {
    email: "Enter Email",
    text: "Enter Text",
    search: "search",
    number: "Enter Number",
    date: "Select Date",
    textarea: "This is the Text area",
    password: "Password",
    file: "Submit File"
  };

  const styles = inputStyles[type] || inputStyles.text;
  const finalplaceholder = placeholder || defaultplaceholder[type];

  /* TEXTAREA */
  if (type === "textarea") {
    return (
      <textarea
        label={label}
        name={name}
        rows={rows}
        placeholder={finalplaceholder}
        value={value}
        onChange={onChange}
        className={`${base} ${styles}`}
        {...props}
      />
    );
  }

  return (
    <div className="relative">
      {type === "search" && (
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          🔍
        </span>
      )}
      <input
        label={label}
        type={type}
        name={name}
        value={value}
        placeholder={finalplaceholder}
        onChange={onChange}
        className={`${base} ${styles}`}
        {...props}
      />
      
    </div>
  );
}

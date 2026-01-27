"use client";

export default function Button({
  children,
  style = "1",
  onClick,
  type = "button",
}) {
  const base = "py-2 rounded-md text-white font-medium transition duration-200";

  const styles = {
    1: " px-4 bg-blue-600 hover:bg-blue-700",
    2: " px-4 bg-gray-600  hover:bg-gray-700",
    3: " px-4 bg-red-600  hover:bg-red-700",
    4: "w-full bg-blue-600 hover:bg-blue-700 transition",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      className={`${base} ${styles[style]}`}
    >
      {children}
    </button>
  );
}

export default function Button({ children, style = "2", onClick }) {
  const base = "px-4 py-2 transition";

  const styles = {
    1: "bg-blue-600 text-white hover:bg-blue-700",
    2: "bg-gray-200 text-black hover:bg-gray-300",
  };

  return (
    <button
      onClick={onClick}
      className={`${base} ${styles[style]}`}
    >
      {children}
    </button>
  );
}

export default function Input({ placeholder, type = "text", value, onChange }) {
  return (
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="p-2 bg-black"
    />
  );
}

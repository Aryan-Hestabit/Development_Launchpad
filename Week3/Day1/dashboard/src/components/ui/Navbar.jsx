export default function Navbar() {
  return (
    <header className="h-14 bg-gray-800 text-white flex items-center justify-between p-5">
      <div>
        <span className="text-lg font-bold">Home</span>
      </div>

      <div className="flex items-center">
        <input
          type="text"
          placeholder="Search for..."
          className="p-2 bg-purple-400 text-black"
        />
        <button className="bg-black py-2 px-4">
          🔍
        </button>
      </div>
    </header>
  );
}

export default function PricingCard({ title, price, description, features }) {
  return (
    <div className="bg-gray-800 rounded-lg p-8 transition transform hover:-translate-y-2 hover:bg-blue-600/30 hover:shadow-xl hover:scale-105">
      <h3 className="text-xl font-semibold">{title}</h3>
      <p className="mt-2 text-gray-200">{description}</p>
      <div className="mt-6 text-3xl font-bold">{price}</div>

      <ul className="mt-6 space-y-2 text-sm text-gray-200">
        {features.map((item) => (
          <li key={item}>✔ {item}</li>
        ))}
      </ul>

      <button className="mt-8 w-full py-3 rounded-md font-medium bg-white text-blue-600 hover:bg-gray-200">
        Get Started
      </button>
    </div>
  );
}

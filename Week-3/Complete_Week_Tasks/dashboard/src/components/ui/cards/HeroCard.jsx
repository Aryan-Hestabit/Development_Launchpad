export default function HeroCard({ title, description }) {
  return (
    <div className="bg-gray-800 p-4 sm:p-5 lg:p-6 rounded-lg transition hover:scale-105">
      <h3 className="sm:text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-gray-300 text-xs sm:text-sm">{description}</p>
    </div>
  );
}

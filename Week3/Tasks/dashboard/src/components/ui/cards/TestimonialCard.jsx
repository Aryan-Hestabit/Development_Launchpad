export default function TestimonialCard({ name, role, text }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm transition hover:shadow-md">
      <p className="text-gray-600">“{text}”</p>
      <div className="mt-4 font-semibold">{name}</div>
      <div className="text-sm text-gray-500">{role}</div>
    </div>
  );
}

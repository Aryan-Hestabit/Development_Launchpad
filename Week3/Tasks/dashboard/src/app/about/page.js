export const metadata = {
  title: "About | StoreFlow",
  description:
    "Learn more about StoreFlow, a modern store management dashboard.",
};

export default function AboutPage() {
  return (
    <div className="p-4 bg-gray-100 min-h-screen">
      <div className="mx-auto bg-white rounded-lg shadow-sm border p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          About StoreFlow
        </h1>

        <p className="text-gray-600 leading-relaxed mb-4">
          StoreFlow is a modern store management dashboard designed to help
          businesses manage inventory, sales, users, and performance from a
          single, intuitive interface.
        </p>

        <p className="text-gray-600 leading-relaxed mb-4">
          Built with Next.js and Tailwind CSS, StoreFlow focuses on clean UI,
          scalability, and ease of use — making it suitable for both small
          shops and large retail chains.
        </p>

        <p className="text-gray-600 leading-relaxed">
          This project demonstrates a frontend-first architecture with reusable
          layouts, component-driven design, and clear separation of concerns.
        </p>
      </div>
    </div>
  );
}

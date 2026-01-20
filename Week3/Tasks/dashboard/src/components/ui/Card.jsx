export default function Card({ title,color, children }) {
  return (
    <div className={`${color} text-white rounded shadow `}>
      {title && (
        <div className="px-4 py-2 font-bold shadow">
          {title}
        </div>
      )}
      <div className="p-4">
        {children}
      </div>
    </div>
  );
}

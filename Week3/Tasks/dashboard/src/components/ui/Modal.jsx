import Button from "./Button";
import Card from "./Card";

export default function Modal({ open, title, children, onClose }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="w-full max-w-md">
        <Card title={title}>
          <div className="mb-4">
            {children}
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={onClose}>
              Confirm
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}

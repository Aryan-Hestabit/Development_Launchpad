import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";

export default function Home() {
  return (
    <div className="space-y-6">

      {/* Page Header */}
      <div className="flex flex-col gap-3">
        <h1 className="text-4xl font-semibold">Dashboard</h1>
        <Badge label="Dashboard" color="blue"/>
      </div>

      {/* Cards Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

        <Card title="Card One" color="bg-blue-400">
          <p className="text-gray-600">
            This is the first dashboard card.
          </p>
        </Card>

        <Card title="Card Two" color="bg-yellow-400">
          <p className="text-gray-600">
            This is the second dashboard card.
          </p>
        </Card>

        <Card title="Card Three" color="bg-red-400">
          <p className="text-gray-600">
            This is the third dashboard card.
          </p>
        </Card>

        <Card title="Card Four" color="bg-green-400">
          <p className="text-gray-600">
            This is the fourth dashboard card.
          </p>
        </Card>

      </div>
    </div>
  );
}

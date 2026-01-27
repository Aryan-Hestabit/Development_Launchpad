import DataTableCard from "@/components/ui/cards/DataTableCard";
import { usersData } from "@/data/user";

export const metadata = {
  title: "Users | Dashboard",
};

export default function UsersPage() {
  return (
    <div className="p-10 bg-gray-100 min-h-screen">
      {/* Breadcrumb */}
      <div className="text-sm text-gray-500 mb-2">
        Users <span className="mx-2">›</span> List
      </div>

      {/* Page Title */}
      <h1 className="text-2xl text-blue-300/70 font-bold mb-6">Users</h1>

      {/* Data Table Card */}
      <DataTableCard
        title="Users"
        hasData={usersData.length > 0}
        columns={["name", "email", "role", "createdAt", "updatedAt"]}
        data={usersData}
      />
    </div>
  );
}

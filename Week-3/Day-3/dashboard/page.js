"use client";

import "@/lib/chart";
import { Bar, Pie, Line, Doughnut } from "react-chartjs-2";
import { useState } from "react";

import Badge from "@/components/ui/Badge";
import GraphCard from "@/components/ui/cards/GraphCard";
import DataTableCard from "@/components/ui/cards/DataTableCard";
import StatCard from "@/components/ui/cards/StatCard";
import Modal from "@/components/ui/Modal";
import Button from "@/components/ui/Button";

import {
  barChartData,
  pieChartData,
  lineChartData,
  doughnutChartData,
} from "@/data/charts";
import { userTableColumns, userTableData } from "@/data/table";

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
};

export default function DashboardPage() {
  const [open, setOpen] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3">
        <Badge type="default">Dashboard</Badge>
      </div>

      <>
        <Button variant="primary" onClick={() => setOpen(true)}>
          Print Report
        </Button>

        <Modal
          isOpen={open}
          title="Delete User"
          onClose={() => setOpen(false)}
          footer={
            <>
              <Button variant="secondary" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button variant="danger">Delete</Button>
            </>
          }
        >
          Are you sure you want to delete this user? This action cannot be
          undone.
        </Modal>
      </>

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Details" color="blue" />
        <StatCard title="Details" color="red" />
        <StatCard title="Details" color="yellow" />
        <StatCard title="Details" color="green" />
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
        <GraphCard title="Details card" color="green" hasData>
          <Line data={lineChartData} options={chartOptions} />
        </GraphCard>

        <GraphCard title="Details card" hasData>
          <Doughnut data={doughnutChartData} options={chartOptions} />
        </GraphCard>
      </section>

      <section>
        <DataTableCard
          title="User Status"
          hasData
          columns={userTableColumns}
          data={userTableData}
        />
      </section>
    </div>
  );
}

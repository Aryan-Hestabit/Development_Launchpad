/* BAR CHART */
export const barChartData = {
  labels: ["January", "February", "March", "April", "May", "June"],
  datasets: [
    {
      label: "Revenue",
      data: [4000, 5200, 6100, 7800, 9500, 15000],
      backgroundColor: "#2563eb",
    },
  ],
};

/* PIE CHART */
export const pieChartData = {
  labels: ["Completed", "Pending", "Failed"],
  datasets: [
    {
      data: [60, 25, 15],
      backgroundColor: ["#16a34a", "#eab308", "#dc2626"],
    },
  ],
};

/* LINE CHART */
export const lineChartData = {
  labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  datasets: [
    {
      label: "Visitors",
      data: [10,20,5,40,25,30,15],
      borderColor: "#2563eb",
      backgroundColor: "rgba(37, 99, 235, 0.2)",
      tension: 0.4,
      fill: true,
      pointRadius: 4,
    },
  ],
};

/* DOUGHNUT CHART */
export const doughnutChartData = {
  labels: ["Desktop", "Mobile", "Tablet", "accessories"],
  datasets: [
    {
      data: [55, 35, 10, 40],
      backgroundColor: ["#2563eb", "#16a34a", "#eab308", "rgb(185, 50, 32)"],
      borderWidth: 1,
    },
  ],
};

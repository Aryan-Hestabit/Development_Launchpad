import Image from "next/image";
import HeroCard from "@/components/ui/cards/HeroCard";
import TestimonialCard from "@/components/ui/cards/TestimonialCard";
import PricingCard from "@/components/ui/cards/PricingCard";
import FeatureCard from "@/components/ui/cards/FeatureCard";

/* -------------------- SEO METADATA -------------------- */
export const metadata = {
  title: {
    default: "StoreFlow – Smart Store Management Dashboard",
    template: "%s | StoreFlow",
  },
  description:
    "StoreFlow helps store owners manage inventory, sales, staff, and analytics from a single powerful dashboard.",
  keywords: [
    "store management software",
    "inventory management",
    "retail dashboard",
    "store analytics",
  ],
  robots: {
    index: true,
    follow: true,
  },
  alternates: {
    canonical: "https://storeflow.com",
  },
  openGraph: {
    title: "StoreFlow – Smart Store Management Dashboard",
    description:
      "Manage inventory, sales, staff, and analytics with a modern store dashboard.",
    url: "https://storeflow.com",
    siteName: "StoreFlow",
    type: "website",
  },
};

/* -------------------- PAGE -------------------- */
export default function LandingPage() {
  return (
    <main className="bg-gray-100 text-gray-800">
      {/* ================= HERO SECTION ================= */}
      <section className="relative text-white overflow-hidden">
        {/* Background Image */}
        <Image
          src="/Hero1.jpeg"
          alt="Store management dashboard"
          width={1920}
          height={705}
          className="object-cover w-full"
          priority
        />

        {/* Content */}
        <div className="absolute inset-0 flex items-center">
          <div className="max-w-6xl mx-auto px-10">
            <h1 className=" text-3xl sm:text-4xl lg:text-5xl font-bold leading-tight">
              Manage Your Store <br />
              <span className="text-blue-400">Smarter, Faster, Better</span>
            </h1>

            <p className=" mt-6 text-sm sm:text-base lg:text-lg text-gray-300 max-w-2xl">
              StoreFlow is an all-in-one store management dashboard to track
              inventory, sales, staff, and performance — all from one place.
            </p>

            <div className="  mt-8 hidden md:grid md:grid-cols-3 lg:grid lg:grid-cols-3 gap-4">
              <HeroCard
                title="Inventory Control"
                description="Track stock levels and avoid shortages."
              />
              <HeroCard
                title="Sales Analytics"
                description="Understand daily, weekly, and monthly sales."
              />
              <HeroCard
                title="Staff Management"
                description="Monitor staff performance and activity."
              />
            </div>
          </div>
        </div>
      </section>

      {/* ================= FEATURES ================= */}
      <section className="py-20 bg-white">
        <div className="max-w-6xl mx-auto px-10">
          <h2 className="text-3xl font-bold mb-10">
            Features Built for Store Owners
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 sm:grid-cols-1 gap-8">
            <FeatureCard
              title="Real-Time Inventory"
              description="Automatically update stock after every sale."
            />
            <FeatureCard
              title="Role-Based Access"
              description="Control what managers and staff can see."
            />
            <FeatureCard
              title="Sales Reports"
              description="Generate detailed reports instantly."
            />
            <FeatureCard
              title="Multi-Store Support"
              description="Manage multiple branches from one dashboard."
            />
            <FeatureCard
              title="Secure Data"
              description="Your business data is encrypted and safe."
            />
            <FeatureCard
              title="Custom Dashboards"
              description="Configure widgets based on your needs."
            />
          </div>
        </div>
      </section>

      {/* ================= PRICING ================= */}
      <section className="relative py-24 text-white">
        {/* Background Image */}
        <div className="absolute inset-0">
          <Image
            src="/image1.jpg"
            alt="Pricing background"
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gray-900/80" />
        </div>

        <div className="relative max-w-6xl mx-auto px-10">
          <h2 className="text-3xl font-bold mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-gray-300 mb-12 max-w-2xl">
            Choose a plan that fits your store size. Upgrade anytime as your
            business grows.
          </p>

          <div className="grid md:grid-cols-3 lg:md:grid-cols-3 sm:grid-cols-1 gap-8">
            <PricingCard
              title="Starter"
              price="₹999 / month"
              description="Best for small shops"
              features={[
                "Inventory tracking",
                "Daily sales report",
                "1 store",
                "Email support",
              ]}
            />

            <PricingCard
              title="Professional"
              price="₹2,499 / month"
              description="For growing businesses"
              features={[
                "Advanced analytics",
                "Staff management",
                "Up to 5 stores",
                "Priority support",
              ]}
            />

            <PricingCard
              title="Enterprise"
              price="Custom"
              description="For large chains"
              features={[
                "Unlimited stores",
                "Custom dashboards",
                "Dedicated manager",
                "24/7 support",
              ]}
            />
          </div>
        </div>
      </section>

      {/* ================= TESTIMONIALS ================= */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-6xl mx-auto px-10">
          <h2 className="text-3xl font-bold mb-10">Trusted by Store Owners</h2>

          <div className="grid sm:grid-cols-1 md:grid-cols-3 lg:grid-cols-3 gap-8">
            <TestimonialCard
              name="Rajesh Kumar"
              role="Retail Store Owner"
              text="StoreFlow reduced our inventory errors by 40%."
            />
            <TestimonialCard
              name="Anita Sharma"
              role="Supermarket Manager"
              text="Sales tracking has never been this easy."
            />
            <TestimonialCard
              name="Mohit Verma"
              role="Franchise Owner"
              text="Managing multiple stores is now effortless."
            />
          </div>
        </div>
      </section>

      {/* ================= FOOTER ================= */}
      <footer className="bg-gray-900 text-gray-300 py-16">
        <div className="max-w-6xl mx-auto px-10 grid grid-cols-3 gap-10">
          <div>
            <h3 className="text-white text-lg font-semibold">StoreFlow</h3>
            <p className="mt-4 text-sm">
              Smart dashboard software designed for modern retail and store
              management.
            </p>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-4">Contact</h4>
            <p>Email: support@storeflow.com</p>
            <p>Phone: +91 98765 43210</p>
          </div>

          <div>
            <h4 className="text-white font-semibold mb-4">Our Team</h4>
            <p className="hover:text-white cursor-pointer">About Us</p>
            <p className="hover:text-white cursor-pointer">LinkedIn</p>
            <p className="hover:text-white cursor-pointer">Twitter</p>
          </div>
        </div>
      </footer>
    </main>
  );
}

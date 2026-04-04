import Image from "next/image";
import Link from "next/link";

export const metadata = {
  title: "Profile | Dashboard",
};

export default function ProfilePage() {
  return (
    <div className="p-8 bg-gray-100 min-h-screen">
      {/* Go Back */}
      <Link
        className="mb-4 text-sm text-blue-600 cursor-pointer"
        href="/dashboard"
      >
        ← Go back
      </Link>

      {/* Profile Card */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Profile Image */}
          <div className="flex justify-center md:justify-start">
            <Image
              src="/Profile.png" // place image in /public
              alt="Profile picture"
              width={300}
              height={300}
              className="rounded-md object-cover"
            />
          </div>

          {/* Basic Info */}
          <div className="space-y-4 border flex flex-col shadow-md p-4 ">
            <div>
              <p className="text-sm text-gray-500">Name</p>
              <p className="font-medium text-gray-800">Nina Valentine</p>
            </div>

            <div>
              <p className="text-sm text-gray-500">Job Title</p>
              <p className="font-medium text-gray-800">Actress</p>
            </div>

            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="text-blue-600">nina_val@example.com</p>
            </div>
          </div>

          {/* Social Links */}
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-500">LinkedIn</p>
              <p className="text-blue-600 cursor-pointer">linkedin.com</p>
            </div>

            <div>
              <p className="text-sm text-gray-500">Twitter</p>
              <p className="text-blue-600 cursor-pointer">www.x.com</p>
            </div>

            <div>
              <p className="text-sm text-gray-500">Facebook</p>
              <p className="text-blue-600 cursor-pointer">facebook.com</p>
            </div>
          </div>
        </div>

        {/* Divider */}
        <hr className="my-6" />

        {/* Bio */}
        <div>
          <p className="text-sm text-gray-500 mb-2">Bio</p>
          <p className="text-gray-700 leading-relaxed">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent
            aliquet odio augue, in dapibus lacus imperdiet ut. Quisque elementum
            placerat neque rhoncus tempus. Cras id suscipit diam, sit amet
            rutrum ipsum. Vestibulum rutrum elit lacinia sapien porta pulvinar.
          </p>
        </div>

        {/* Divider */}
        <hr className="my-6" />

        {/* Edit Profile */}
        <div className="text-blue-600 text-sm cursor-pointer">Edit Profile</div>
      </div>
    </div>
  );
}

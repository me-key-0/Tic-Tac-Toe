import React from "react";

const Sidebar = () => {
  return (
    <aside className="bg-white w-64 p-4 border-r border-gray-300 h-screen">
      <ul className="space-y-4">
        <li>
          <button className="text-lg font-medium w-full text-left">
            Leaderboard
          </button>
        </li>
        <li>
          <button className="text-lg font-medium w-full text-left">
            Account
          </button>
        </li>
        <li>
          <button className="text-lg font-medium w-full text-left">
            Chats
          </button>
        </li>
        <li>
          <button className="text-lg font-medium w-full text-left">
            Settings
          </button>
        </li>
      </ul>
    </aside>
  );
};

export default Sidebar;

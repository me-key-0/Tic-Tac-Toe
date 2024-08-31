import React from "react";

const Header = () => {
  return (
    <header className="bg-white rounded-lg shadow p-6 flex justify-between items-center mb-6">
      <div className="flex items-center space-x-4">
        <span className="text-xl">👤</span>
        <h1 className="text-2xl font-bold">Tic Tac Toe</h1>
      </div>
      <div className="flex space-x-4 text-xl">
        <span>🔔</span>
        <span>⚙️</span>
      </div>
    </header>
  );
};

export default Header;

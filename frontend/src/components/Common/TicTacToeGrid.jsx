import React from "react";

const TicTacToeGrid = () => {
  return (
    <div className="flex justify-center items-center h-[calc(100vh-200px)]">
      <div className="grid grid-cols-3 grid-rows-3 gap-2">
        <div className="bg-gray-400 rounded-lg border-2 border-black w-24 h-24"></div>
        <div className="bg-gray-400 rounded-lg border-2 border-black w-24 h-24"></div>
        <div className="bg-gray-400 rounded-lg border-2 border-black w-24 h-24"></div>
        <div className="bg-gray-400 rounded-lg border-2 border-black w-24 h-24"></div>
        <div className="bg-gray-400 rounded-lg border-2 border-black w-24 h-24"></div>
        <div className="bg-gray-400 rounded-lg border-2 border-black w-24 h-24"></div>
      </div>
    </div>
  );
};

export default TicTacToeGrid;

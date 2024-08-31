import React, { useState, useEffect } from "react";
import { saveGameResult, getCurrentGameStatus } from "../../api/game";

const TicTacToeBoard = ({ player, opponent }) => {
  const [board, setBoard] = useState(Array(9).fill(null));
  const [isPlayerTurn, setIsPlayerTurn] = useState(true);
  const [status, setStatus] = useState("Your turn");

  useEffect(() => {
    // Fetch current game status from API
    getCurrentGameStatus().then((data) => {
      setBoard(data.board);
      setIsPlayerTurn(data.isPlayerTurn);
    });
  }, []);

  const handleClick = (index) => {
    if (!board[index]) {
      const newBoard = board.slice();
      newBoard[index] = isPlayerTurn ? "X" : "O";
      setBoard(newBoard);
      setIsPlayerTurn(!isPlayerTurn);

      // Save the game result after every move
      saveGameResult(newBoard, isPlayerTurn ? "X" : "O");
    }
  };

  const renderSquare = (index) => {
    return (
      <button
        className="w-24 h-24 text-4xl font-bold"
        onClick={() => handleClick(index)}
      >
        {board[index]}
      </button>
    );
  };

  return (
    <>
      <div className="flex justify-center items-center h-screen border-3 border-black">
        <div className="grid grid-rows-3 grid-flow-col gap-1">
          {Array(9)
            .fill(null)
            .map((_, index) => renderSquare(index))}
        </div>
      </div>
      <div className="mt-4">{status}</div>
    </>
  );
};

export default TicTacToeBoard;

import React from "react";
import TicTacToeGrid from '../components/Common/TicTacToeGrid'; // or wherever the correct path is

const Home = () => {
    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold mb-4">Welcome to Tic Tac Toe</h1>
            <TicTacToeGrid />
        </div>
    );
};

export default Home;

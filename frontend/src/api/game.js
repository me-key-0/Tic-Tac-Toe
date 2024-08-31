// src/api/game.js

export const saveGameResult = async (gameId, result) => {
    // Replace with actual API call to save the game result
    try {
      const response = await fetch(`/api/games/${gameId}/result`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ result }),
      });
  
      if (!response.ok) {
        throw new Error('Failed to save game result');
      }
  
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error saving game result:', error);
      throw error;
    }
  };
  
  // Ensure other functions, like getCurrentGameStatus, are also exported here
  export const getCurrentGameStatus = async (gameId) => {
    try {
      const response = await fetch(`/api/games/${gameId}/status`);
      if (!response.ok) {
        throw new Error('Failed to fetch game status');
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching game status:', error);
      throw error;
    }
  };
  
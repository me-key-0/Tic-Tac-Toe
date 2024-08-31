import React from "react";
import {
  Route,
  createBrowserRouter,
  createRoutesFromElements,
  RouterProvider,
} from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import Home from "./pages/Home";
import Account from "./pages/Account";
import LeadersBoard from "./pages/LeadersBoard";
import Chats from "./pages/Chats";
import History from "./pages/History";
import NotFoundPage from "./pages/NotFoundPage";

// Define the router and routes
const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<MainLayout />}>
      <Route index element={<Home />} />
      <Route path="account" element={<Account />} />
      <Route path="leaderboard" element={<LeadersBoard />} />
      <Route path="chats" element={<Chats />} />
      <Route path="history" element={<History />} />
      <Route path="*" element={<NotFoundPage />} />
    </Route>
  )
);

const App = () => {
  return <RouterProvider router={router} />;
};

export default App;

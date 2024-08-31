import { Route, Navigate } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import MainLayout from "./layouts/MainLayout";
import Home from "./pages/Home";
import Account from "./pages/Account";
import Leaderboard from "./pages/Leaderboard";
import Chats from "./pages/Chats";
import History from "./pages/History";
import NotFoundPage from "./pages/NotFoundPage";
import Login from "./components/Auth/Login";
import Signup from "./components/Auth/Signup";

const ProtectedRoute = ({ element, ...rest }) => {
  const { user } = useAuth();
  return user ? <Route {...rest} element={element} /> : <Navigate to="/login" />;
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        path: "/",
        element: <Home />,
      },
      {
        path: "/account",
        element: <ProtectedRoute element={<Account />} />,
      },
      {
        path: "/leaderboard",
        element: <Leaderboard />,
      },
      {
        path: "/chats",
        element: <ProtectedRoute element={<Chats />} />,
      },
      {
        path: "/history",
        element: <ProtectedRoute element={<History />} />,
      },
      {
        path: "/login",
        element: <Login />,
      },
      {
        path: "/signup",
        element: <Signup />,
      },
      {
        path: "*",
        element: <NotFoundPage />,
      },
    ],
  },
]);

export default router;

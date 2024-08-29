import { IoPerson } from "react-icons/io5";
import { RiLockPasswordFill } from "react-icons/ri";
import { MdEmail } from "react-icons/md";
import { useState } from "react";

const LoginSignup = () => {
  const [action, setAction] = useState("Sign Up");
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const validate = () => {
    const newErrors = {};
    if (action === "Sign Up" && !formData.name) {
      newErrors.name = "Name is required";
    }
    if (!formData.email) {
      newErrors.email = "Email is required";
    }
    if (!formData.password) {
      newErrors.password = "Password is required";
    }
    return newErrors;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    setLoading(true);

    // Simulate form submission
    setTimeout(() => {
      setLoading(false);
      alert(`${action} successful!`);
    }, 1000);
  };

  return (
    <div className="bg-banner-image bg-cover h-[100vh]">
      <div className="flex justify-center items-center h-full">
        <div
          className="lg:w-[450px] bg-white py-20 px-10"
          style={{ borderRadius: "20px" }}
        >
          <h1 className="text-4xl text-blue-900 text-center mb-6 transition-all">
            {action}
          </h1>
          <form onSubmit={handleSubmit}>
            {action === "Sign Up" && (
              <div className="bg-gray-200 flex items-center gap-5 my-4 p-4 rounded transition-all">
                <IoPerson className="text-gray-700 text-xl" />
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="bg-transparent border-none outline-none w-full"
                  placeholder="Your Name"
                  aria-label="Your Name"
                />
              </div>
            )}
            {errors.name && <p className="text-red-500">{errors.name}</p>}

            <div className="bg-gray-200 flex items-center gap-5 my-4 p-4 rounded">
              <MdEmail className="text-gray-700 text-xl" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="bg-transparent border-none outline-none w-full"
                placeholder="Your Email"
                aria-label="Your Email"
              />
            </div>
            {errors.email && <p className="text-red-500">{errors.email}</p>}

            <div className="bg-gray-200 flex items-center gap-5 my-4 p-4 rounded">
              <RiLockPasswordFill className="text-gray-700 text-xl" />
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="bg-transparent border-none outline-none w-full"
                placeholder="Your Password"
                aria-label="Your Password"
              />
            </div>
            {errors.password && (
              <p className="text-red-500">{errors.password}</p>
            )}

            {action === "Login" && (
              <div className="text-center my-4">
                <p>
                  Forgot Password?{" "}
                  <span className="text-blue-900 cursor-pointer">
                    Click Here
                  </span>
                </p>
              </div>
            )}

            <div className="flex justify-center gap-8 mt-10">
              <button
                type="button"
                className={`text-xl text-white py-2 w-36 rounded-3xl ${
                  action === "Sign Up" ? "bg-blue-900" : "bg-gray-200"
                }`}
                onClick={() => setAction("Sign Up")}
              >
                Sign Up
              </button>
              <button
                type="button"
                className={`text-xl text-white py-2 w-36 rounded-3xl ${
                  action === "Login" ? "bg-blue-900" : "bg-gray-200"
                }`}
                onClick={() => setAction("Login")}
              >
                Login
              </button>
            </div>

            <div className="flex justify-center mt-10">
              <button
                type="submit"
                className="text-xl text-white py-2 w-full rounded-3xl bg-blue-900"
                disabled={loading}
              >
                {loading ? "Processing..." : action}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginSignup;

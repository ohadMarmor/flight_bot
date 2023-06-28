import { useNavigate } from "react-router-dom";
import { Link } from 'react-router-dom';
import './Home.css';

export const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="container">
      <div className="content">
        <div>Welcome To SporTrip!</div>
        <div>Let's Find Your Dream Tour</div>
        <button onClick={() => navigate('login')}>Login</button>
        <div className="register-link">
          Don't have an account? <Link to="/register">Register</Link>
        </div>
      </div>
    </div>
  );
};

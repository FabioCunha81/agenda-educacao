import { ChevronRight, Eye, EyeOff, Lock, Mail, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client.js";
import cardImage from "../assets/Captura de tela 2026-06-17 124452.jpg";
import eventsBarsImage from "../assets/acoes-eventos-bares.png";
import companyLectureImage from "../assets/palestra-empresa.jpeg";
import leiSecaLogo from "../assets/operacao-lei-seca-logo.png";
import { useAuth } from "../context/AuthContext.jsx";

const showcaseCards = [
  {
    title: "Palestra Empresa",
    image: companyLectureImage,
    imagePosition: "center",
    variant: "left",
  },
  {
    title: "Educação Escola Nota 10 Infantil",
    imagePosition: "left center",
    variant: "active",
  },
  {
    title: "Ações em eventos e bares",
    image: eventsBarsImage,
    imagePosition: "center",
    variant: "right",
  },
];

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = await api("/auth/login/", {
        method: "POST",
        body: JSON.stringify({ email: email.trim(), password }),
        redirectOnUnauthorized: false,
      });
      login(payload);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const recover = async () => {
    setError("");
    try {
      const payload = await api("/auth/password-reset/", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
      setError(payload.detail);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <main className="login-page">
      <section className="login-panel lei-seca-login">
        <aside className="login-showcase" aria-label="Operação Lei Seca">
          <div className="showcase-logo">
            <img src={leiSecaLogo} alt="Operação Lei Seca" />
          </div>
          <div className="login-card-stack" aria-label="Ações educativas">
            {showcaseCards.map((card) => (
              <article className={`login-action-card ${card.variant}`} key={card.title}>
                <img src={card.image || cardImage} alt="" style={{ objectPosition: card.imagePosition }} />
                <h2>{card.title}</h2>
              </article>
            ))}
          </div>
        </aside>

        <form onSubmit={submit} className="login-form">
          <div className="login-brand">
            <div>
              <span className="eyebrow">Operação Lei Seca</span>
              <h1>SISTEMA INTEGRADO DA EDUCAÇÃO</h1>
              <p>Gestão da educação da Operação Lei Seca</p>
            </div>
          </div>
          <label>
            E-mail
            <span className="input-icon">
              <Mail size={18} />
              <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="Digite seu e-mail" autoComplete="username" required />
            </span>
          </label>
          <label>
            Senha
            <span className="input-icon">
              <Lock size={18} />
              <input value={password} onChange={(e) => setPassword(e.target.value)} type={showPassword ? "text" : "password"} placeholder="Digite sua senha" autoComplete="current-password" required />
              <button
                className="input-action-button"
                type="button"
                onClick={() => setShowPassword((value) => !value)}
                aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                title={showPassword ? "Ocultar senha" : "Mostrar senha"}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </span>
          </label>
          <div className="login-options">
            <label className="remember-option">
              <input type="checkbox" />
              Lembrar meu acesso
            </label>
            <button className="link-button" type="button" onClick={recover}>
              Esqueci minha senha
            </button>
          </div>
          {error && <div className="alert">{error}</div>}
          <button className="login-submit" disabled={loading}>
            <Lock size={22} />
            {loading ? "Entrando..." : "Entrar"}
            <ChevronRight size={24} />
          </button>
          <div className="login-restricted">
            <ShieldCheck size={22} />
            <span>Acesso restrito aos usuários autorizados.</span>
          </div>
        </form>
      </section>
    </main>
  );
}

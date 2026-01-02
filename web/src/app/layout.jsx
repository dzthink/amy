import "./globals.css";
import "@copilotkit/react-ui/styles.css";

export const metadata = {
  title: "Amy Agent Console",
  description: "Agent chat workspace UI",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

export const metadata = {
  title: "PixelDraft — screenshot to React",
  description: "Turn a UI screenshot into editable React + Tailwind.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

export const metadata = {
  title: 'TSAR Dashboard',
  description: 'TSAR security posture',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

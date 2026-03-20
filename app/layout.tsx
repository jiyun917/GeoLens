import "./globals.css";
import { GeistSans } from "geist/font/sans";
import { Toaster } from "sonner";
import { cn } from "@/lib/utils";
import { TaskProvider } from "./providers/TaskProvider";
import { SettingsProvider } from "./providers/SettingsProvider";
import { ManualProvider } from "./providers/ManualProvider";
import { ReportProvider } from "./providers/ReportProvider";
import { Inter } from "next/font/google";

export const metadata = {
  title: "GeoLens",
  description:
    "Share your screen with AI. Get guided through anything.",
  icons: {
    icon: "/icon.png",
    shortcut: "/icon.png",
    apple: "/icon.png",
  },
};

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-inter",
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={cn(
          GeistSans.className,
          inter.variable,
          "antialiased dark",
          "bg-background"
        )}
      >
        <Toaster position="top-center" richColors />
        <SettingsProvider>
          <ManualProvider>
            <TaskProvider>
              <ReportProvider>{children}</ReportProvider>
            </TaskProvider>
          </ManualProvider>
        </SettingsProvider>
      </body>
    </html>
  );
}

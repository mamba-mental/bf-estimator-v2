import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from "@/components/ui/toast"
import { useToast } from "@/components/ui/use-toast"

export function Toaster() {
  const { toasts } = useToast()

  // Show only the most recent toast to prevent stacking
  const mostRecentToast = toasts.length > 0 ? toasts[0] : null;

  return (
    <ToastProvider>
      {mostRecentToast && (function () {
        const { id, title, description, action, ...props } = mostRecentToast;
        return (
          <Toast key={id} {...props}>
            <div className="grid gap-1">
              {title && <ToastTitle>{title}</ToastTitle>}
              {description && (
                <ToastDescription>{description}</ToastDescription>
              )}
            </div>
            {action}
            <ToastClose />
          </Toast>
        );
      })()}
      <ToastViewport />
    </ToastProvider>
  )
}
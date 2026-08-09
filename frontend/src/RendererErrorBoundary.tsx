import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

type Props = {
  children: ReactNode;
  resetKey: string;
};

type State = { failed: boolean };

export default class RendererErrorBoundary extends Component<Props, State> {
  state: State = { failed: false };

  static getDerivedStateFromError(): State {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Challenge renderer failed", error.message, info.componentStack);
  }

  componentDidUpdate(previous: Props) {
    if (this.state.failed && previous.resetKey !== this.props.resetKey) {
      this.setState({ failed: false });
    }
  }

  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <div className="renderer-error" role="alert">
        <AlertTriangle size={20} aria-hidden="true" />
        <strong>This workspace mode couldn’t load.</strong>
        <span>Your interview session is still active. Retry the renderer or use the other challenge tab.</span>
        <button onClick={() => this.setState({ failed: false })}>
          <RefreshCw size={14} aria-hidden="true" /> Retry renderer
        </button>
      </div>
    );
  }
}

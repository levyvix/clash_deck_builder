import React, { Component, ErrorInfo, ReactNode } from 'react';
import '../styles/ErrorBoundary.css';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error details for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="error-boundary">
          <div className="error-boundary__container">
            <h1 className="error-boundary__title">Oops! Something went wrong</h1>
            <p className="error-boundary__message">
              We're sorry, but something unexpected happened. Please try refreshing the page.
            </p>
            
            {this.state.error && (
              <details className="error-boundary__details">
                <summary className="error-boundary__summary">Error details</summary>
                <pre className="error-boundary__error-text">
                  {this.state.error.toString()}
                  {this.state.errorInfo && (
                    <>
                      {'\n\n'}
                      {this.state.errorInfo.componentStack}
                    </>
                  )}
                </pre>
              </details>
            )}
            
            <div className="error-boundary__actions">
              <button
                className="error-boundary__button error-boundary__button--primary"
                onClick={() => window.location.reload()}
              >
                Refresh Page
              </button>
              <button
                className="error-boundary__button error-boundary__button--secondary"
                onClick={this.handleReset}
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

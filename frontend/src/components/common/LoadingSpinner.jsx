function LoadingSpinner({ message = '載入中...' }) {
    return (
      <div className="flex flex-col items-center justify-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-primary"></div>
        <p className="mt-4 text-gray-600">{message}</p>
      </div>
    );
  }
  
  export default LoadingSpinner;
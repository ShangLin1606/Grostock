function Footer() {
  return (
    <footer className="bg-gray-900 text-text py-6">
      <div className="container text-center">
        <p>© 2025 Grostock. All rights reserved.</p>
        <p className="mt-2">
          <a href="/about" className="hover:text-primary">關於我們</a> | 
          <a href="#" className="hover:text-primary ml-2">隱私政策</a> | 
          <a href="#" className="hover:text-primary ml-2">聯繫我們</a>
        </p>
      </div>
    </footer>
  );
}

export default Footer;
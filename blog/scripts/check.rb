# Check local targets after a build, including a project-site base path.
require "cgi"
require "pathname"
require "uri"

root = Pathname.new(ARGV.fetch(0, "_site")).expand_path
baseurl = ARGV.fetch(1, "").sub(%r{/$}, "")
abort "Missing build: #{root}" unless root.directory?
errors = []
%w[index.html about/index.html experiments/index.html atlas/index.html experiments/manifest.json feed.xml 404.html assets/style.css].each do |path|
  errors << "Missing #{path}" unless root.join(path).file?
end
%w[Gemfile Gemfile.lock README.md scripts templates _drafts experiment-guides.tsv experiment-figures.json atlas.json].each do |path|
  errors << "Authoring file leaked: #{path}" if root.join(path).exist?
end
root.glob("**/*.html").sort.each do |file|
  file.read.scan(/(?:href|src)=["']([^"']+)["']/).flatten.each do |raw|
    url = CGI.unescapeHTML(raw)
    next if url.start_with?("#", "//") || url.match?(/\A[a-z][a-z0-9+.-]*:/i)

    path = URI::DEFAULT_PARSER.unescape(url.split(/[?#]/).first.to_s)
    next if path.empty?

    if path.start_with?("/")
      if !baseurl.empty? && path != baseurl && !path.start_with?(baseurl + "/")
        errors << "#{file.relative_path_from(root)}: link escapes baseurl: #{raw}"
        next
      end
      target = root.join(path.delete_prefix(baseurl).delete_prefix("/"))
    else
      target = file.dirname.join(path).cleanpath
    end
    target = target.join("index.html") if target.directory?
    errors << "#{file.relative_path_from(root)}: missing target: #{raw}" unless target.file?
  end
end
abort errors.join("\n") unless errors.empty?
puts "Checked #{root.glob('**/*.html').size} HTML pages; local links and required outputs OK."

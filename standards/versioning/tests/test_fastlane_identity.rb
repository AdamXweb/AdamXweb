require "tmpdir"
require "fileutils"

kit = File.expand_path("..", __dir__)
Dir.mktmpdir do |root|
  FileUtils.cp_r(File.join(kit, "Scripts"), File.join(root, "Scripts"))
  require File.join(root, "Scripts/build_identity")
  saved = ENV.to_h
  begin
    [nil, ""].each do |input|
      input.nil? ? ENV.delete("BUILD_NUMBER") : ENV["BUILD_NUMBER"] = input
      values = BuildIdentity.settings("release").to_h { |value| value.split("=", 2) }
      raise "Missing/empty input must generate a stamp" unless values["BUILD_NUMBER"].match?(/\A[0-9]{4}\.[0-9]{4}\.[0-9]{4}\z/)
      raise "Release provenance must be minimal" unless values["BUILD_SHA"] == "" && values["BUILD_BRANCH"] == ""
    end
    ENV["BUILD_NUMBER"] = "2026.0930.0000"
    ENV.delete("BUILD_TIMESTAMP")
    raise "Explicit override lost" unless BuildIdentity.settings("release").include?("BUILD_NUMBER=2026.0930.0000")
    raise "Override timestamp differs" unless BuildIdentity.settings("release").include?("BUILD_TIMESTAMP=2026-09-30T00:00:00Z")
    ENV["BUILD_NUMBER"] = "0"
    begin
      BuildIdentity.settings("release")
      raise "Zero must never ship"
    rescue RuntimeError => error
      raise unless error.message.start_with?("Invalid BUILD_NUMBER")
    end
  ensure
    ENV.replace(saved)
  end
end
puts "Fastlane adapter passed: missing/empty input, release redaction, override, invalid sentinel"

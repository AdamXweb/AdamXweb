# Shared Fastlane adapter. Capture once, then reuse these settings for every
# artifact in a lane. Empty BUILD_NUMBER input means generate, never build 0.
require "open3"
require "shellwords"
require "time"

module BuildIdentity
  def self.settings(channel)
    root = File.expand_path("..", __dir__)
    output, result = Open3.capture2(
      { "BUILD_CHANNEL" => channel }, "bash", File.join(__dir__, "buildinfo.sh"), chdir: root
    )
    raise "Could not generate build identity" unless result.success?
    values = output.lines.map(&:strip).reject(&:empty?)
    override = ENV["BUILD_NUMBER"].to_s
    unless override.empty?
      raise "Invalid BUILD_NUMBER: #{override}" unless override.match?(/\A[0-9]{4}\.[0-9]{4}\.[0-9]{4}\z/)
      timestamp = ENV["BUILD_TIMESTAMP"].to_s
      timestamp = Time.strptime(override + " +0000", "%Y.%m%d.%H%M %z").utc.iso8601 if timestamp.empty?
      raise "BUILD_TIMESTAMP differs from BUILD_NUMBER" unless Time.iso8601(timestamp).utc.strftime("%Y.%m%d.%H%M") == override
      values.reject! { |value| value.start_with?("BUILD_NUMBER=", "BUILD_TIMESTAMP=") }
      values << "BUILD_NUMBER=#{override}"
      values << "BUILD_TIMESTAMP=#{timestamp}"
    end
    values
  end

  def self.xcargs(channel)
    settings(channel).map(&:shellescape).join(" ")
  end
end

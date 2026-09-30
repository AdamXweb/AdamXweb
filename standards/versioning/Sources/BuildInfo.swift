import Foundation

/// Provenance for the running build, read from Info.plist keys stamped by
/// Scripts/buildinfo.sh at build time.
public enum BuildInfo {
    private static func value(_ key: String) -> String? {
        guard let v = Bundle.main.object(forInfoDictionaryKey: key) as? String,
              !v.isEmpty, v != "unknown"
        else { return nil }
        return v
    }

    public static let marketingVersion = value("CFBundleShortVersionString") ?? "0.0.0"
    public static let buildNumber      = value("CFBundleVersion") ?? "0"
    public static let sha              = value("BuildSHA")
    public static let branch           = value("BuildBranch")
    public static let diffID           = value("BuildDiffID")
    public static let timestamp        = value("BuildTimestamp")
    public static let channel          = value("BuildChannel") ?? "unknown"
    public static let isDirty          = value("BuildDirty") == "YES"
    public static let dirtyFiles       = Int(value("BuildDirtyFiles") ?? "") ?? 0
    public static let isTagged         = value("BuildTagged") == "YES"

    /// Clean tree, sitting on a release tag, built for release. Described by
    /// its version alone.
    public static var isRelease: Bool { channel == "release" && isTagged && !isDirty }

    /// The single line shown in Settings ▸ About.
    public static var summary: String {
        isRelease ? marketingVersion
                  : "\(marketingVersion) (\(buildNumber))"
    }

    /// Extra lines shown under `summary` on non-release builds. Empty on a
    /// release build.
    public static var detail: [String] {
        guard !isRelease else { return [] }
        var lines: [String] = []
        if let sha {
            lines.append([sha, branch].compactMap(\.self).joined(separator: " · "))
        }
        if isDirty {
            let d = diffID.map { " · diff \($0)" } ?? ""
            lines.append("\(dirtyFiles) uncommitted change\(dirtyFiles == 1 ? "" : "s")\(d)")
        }
        if sha == nil && !isDirty { lines.append("built from Xcode — no commit recorded") }
        return lines
    }

    /// Everything, one string, for the copy-to-clipboard button.
    public static var report: String {
        ([summary] + detail + ["channel \(channel)", timestamp ?? ""])
            .filter { !$0.isEmpty }
            .joined(separator: "\n")
    }
}

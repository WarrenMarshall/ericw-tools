// Experimental Phase 7: decisions use retained binary64 halfspaces.
// Winding/residual helpers below validate approximate construction only.
#pragma once
#include <qbsp/winding.hh>
#include <qbsp/halfspace.hh>
#include <common/aabb.hh>
#include <limits>
#include <cmath>

namespace supported_geometry {
inline p6::Plane coefficients(const qplane3d &p) { return {p.normal[0],p.normal[1],p.normal[2],p.dist}; }
// No caller may replace an unresolved result with SOLID/EMPTY or deletion.
inline p6::Result region(const std::vector<p6::Plane> &supports) {
    p6::Stats stats;
    return p6::analyze(supports, stats);
}
inline int dimension(const std::vector<p6::Plane> &supports) {
    auto r = region(supports);
    if (r.dimension == -2) throw std::runtime_error("PHASE7 NUMERICAL_UNCERTAINTY: " + r.reason);
    return r.dimension;
}

inline bool portal_has_area(const std::vector<qplane3d> &supports, const qplane3d &plane) {
    std::vector<p6::Plane> region;
    for (auto &p : supports) region.push_back(coefficients(p));
    auto q = coefficients(plane);
    region.push_back(q); region.push_back(p6::opposite(q));
    return dimension(region) == 2;
}
struct distance_t { long double value, error; };
inline distance_t distance(const qvec3d &p, const qplane3d &plane)
{
    long double value = -static_cast<long double>(plane.dist);
    long double magnitude = std::abs(value);
    for (int i = 0; i < 3; ++i) {
        long double product = static_cast<long double>(p[i]) * plane.normal[i];
        value += product;
        magnitude += std::abs(product);
    }
    // Three products, three additions, and an enclosing rounded magnitude sum.
    const long double u = std::numeric_limits<long double>::epsilon();
    return {value, (8 * u / (1 - 8 * u)) * magnitude};
}

// Exclusive broad-phase answers require separation of the complete box.
// Uncertainty includes contact and deliberately returns BOTH.
inline int box_side(const aabb3d &bounds, const qplane3d &plane)
{
    std::array<double,3> lo, hi;
    for (int i = 0; i < 3; ++i) {
        lo[i] = plane.normal[i] < 0 ? bounds.maxs()[i] : bounds.mins()[i];
        hi[i] = plane.normal[i] < 0 ? bounds.mins()[i] : bounds.maxs()[i];
    }
    p6::Stats stats;
    p6::Plane q{plane.normal[0],plane.normal[1],plane.normal[2],plane.dist};
    auto minimum = p6::point_side(q,lo,stats,p6::Mode::filtered);
    auto maximum = p6::point_side(q,hi,stats,p6::Mode::filtered);
    if (minimum && *minimum > 0) return 1;
    if (maximum && *maximum < 0) return 2;
    return 3;
}

// Existing polylib constructor, at the precision already used for brush faces.
// Retained constraints, rather than a clipped/rounded winding, define the face.
inline std::optional<winding_t> reconstruct_boundary(const qplane3d &plane,
    const std::vector<qplane3d> &supports, double extent)
{
    using precise_winding_t = polylib::winding_base_t<polylib::winding_storage_heap_t<long double>>;
    std::optional<precise_winding_t> w = precise_winding_t::from_plane(
        qplane3<long double>(plane), static_cast<long double>(extent));
    for (auto &p : supports) {
        if ((p.normal == plane.normal && p.dist == plane.dist) ||
            (p.normal == -plane.normal && p.dist == -plane.dist)) continue;
        if (!w) return std::nullopt;
        w = w->clip_front(-qplane3<long double>(p), 0, true);
    }
    if (!w) return std::nullopt;
    winding_t result;
    for (auto &point : *w) result.push_back(qvec3d(point));
    return result;
}

enum class rank_t { area, lower_dimensional, uncertain };
inline rank_t winding_rank(const winding_t &w, const qplane3d &plane)
{
    if (w.size() < 3) return rank_t::lower_dimensional;
    long double area = 0, scale = 0;
    for (size_t i = 2; i < w.size(); ++i) {
        long double a[3], b[3], sa[3], sb[3];
        for (int k = 0; k < 3; ++k) {
            a[k] = static_cast<long double>(w[i-1][k]) - w[0][k];
            b[k] = static_cast<long double>(w[i][k]) - w[0][k];
            sa[k] = std::abs(static_cast<long double>(w[i-1][k])) + std::abs(static_cast<long double>(w[0][k]));
            sb[k] = std::abs(static_cast<long double>(w[i][k])) + std::abs(static_cast<long double>(w[0][k]));
        }
        for (int k = 0; k < 3; ++k) {
            int j = (k+1)%3, l = (k+2)%3;
            area += (a[j]*b[l] - a[l]*b[j]) * plane.normal[k];
            scale += (sa[j]*sb[l] + sa[l]*sb[j]) * std::abs(static_cast<long double>(plane.normal[k]));
        }
    }
    const long double u = std::numeric_limits<long double>::epsilon();
    const long double operations = 32 * static_cast<long double>(w.size());
    long double error = operations*u/(1-operations*u)*scale;
    if (!std::isfinite(area) || !std::isfinite(error)) return rank_t::uncertain;
    if (std::abs(area) > error) return rank_t::area;
    return rank_t::uncertain; // small is not proof of degeneracy
}

// Selective construction of a target-area-bearing section, reusing Phase 6's
// feasible homogeneous candidates. This does not change any existence decision.
inline std::optional<winding_t> reconstruct_section(const qplane3d &plane,
    const std::vector<qplane3d> &supports)
{
    std::vector<p6::Plane> ps;
    for (auto &p : supports) ps.push_back(coefficients(p));
    auto q = coefficients(plane);
    ps.push_back(q); ps.push_back(p6::opposite(q));
    auto target = ps;
    for (auto &p : target) for (double &v : p) v = static_cast<float>(v);
    if (dimension(target) != 2 || dimension(ps) != 2) return std::nullopt;
    std::sort(ps.begin(),ps.end()); ps.erase(std::unique(ps.begin(),ps.end()),ps.end());
    using point_t = std::array<p6::Q,3>;
    std::vector<point_t> points;
    p6::Stats stats;
    p6::vertices(ps,stats,p6::Mode::filtered,[&](p6::Candidate &v) {
        auto h = v.rational();
        point_t point{h[0]/h[3],h[1]/h[3],h[2]/h[3]};
        if (std::find(points.begin(),points.end(),point)==points.end()) points.push_back(std::move(point));
        return false;
    });
    if (points.size()<3) return std::nullopt;
    int axis=0;
    for (int i=1;i<3;++i) if (std::abs(plane.normal[i])>std::abs(plane.normal[axis])) axis=i;
    int u=(axis+1)%3, v=(axis+2)%3;
    p6::Q cu=0,cv=0;
    for (auto &p : points) { cu+=p[u]; cv+=p[v]; }
    cu/=points.size();cv/=points.size();
    auto upper = [&](const point_t &p) { return p[v]>cv || (p[v]==cv && p[u]>=cu); };
    std::sort(points.begin(),points.end(),[&](const point_t &a,const point_t &b) {
        if (upper(a)!=upper(b)) return upper(a)>upper(b);
        p6::Q cross=(a[u]-cu)*(b[v]-cv)-(a[v]-cv)*(b[u]-cu);
        return cross>0;
    });
    if (plane.normal[axis]>0) std::reverse(points.begin(),points.end());
    winding_t result;
    std::vector<point_t> rounded;
    for (auto &p : points) {
        qvec3d point{p[0].get_d(),p[1].get_d(),p[2].get_d()};
        result.push_back(point);
        rounded.push_back({p6::Q(point[0]),p6::Q(point[1]),p6::Q(point[2])});
    }
    // Narrowing must preserve distinct vertices and every projected orientation.
    // Reject a collapse or changed incidence instead of welding or perturbing it.
    for (size_t a=0;a<points.size();++a) for (size_t b=a+1;b<points.size();++b) {
        if (rounded[a]==rounded[b]) return std::nullopt;
        for (size_t c=b+1;c<points.size();++c) {
            auto orientation = [&](const std::vector<point_t> &p) {
                p6::Q cross=(p[b][u]-p[a][u])*(p[c][v]-p[a][v])-(p[b][v]-p[a][v])*(p[c][u]-p[a][u]);
                return p6::qsign(cross);
            };
            if (orientation(points)!=orientation(rounded)) return std::nullopt;
        }
    }
    return result;
}

// A backward-residual check, not a forward bound on an ill-conditioned solve.
inline bool boundary_residual_ok(const qvec3d &p, const qplane3d &plane, bool on_plane)
{
    auto d = distance(p, plane);
    long double scale = std::abs(static_cast<long double>(plane.dist));
    for (int i=0; i<3; ++i) scale += std::abs(static_cast<long double>(p[i])*plane.normal[i]);
    const long double u = std::numeric_limits<double>::epsilon();
    long double bound = 32*u/(1-32*u)*scale;
    return on_plane ? std::abs(d.value) <= bound : d.value <= bound;
}
} // namespace supported_geometry

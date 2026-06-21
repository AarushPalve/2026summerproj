import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  CircularProgress,
  Alert,
  TextField,
  Table,
  TableBody,
  TableRow,
  TableCell,
  TableHead,
  TableContainer,
  Pagination,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Chip,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import { Search as SearchIcon, Sort as SortIcon } from '@mui/icons-material';
import { getAllTeams, getTeamRankings, compareTeams } from '../services/api';
import { TeamRanking } from '../types';

const TeamsPage: React.FC = () => {
  const [teams, setTeams] = useState<TeamRanking[]>([]);
  const [filteredTeams, setFilteredTeams] = useState<TeamRanking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('epa');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [selectedTeams, setSelectedTeams] = useState<number[]>([]);
  const [comparisonResults, setComparisonResults] = useState<any>(null);
  const [comparisonLoading, setComparisonLoading] = useState(false);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        setLoading(true);
        const response = await getTeamRankings({ sortBy, order: sortOrder });
        setTeams(response.data);
        setFilteredTeams(response.data);
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load teams';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchTeams();
  }, [sortBy, sortOrder]);

  useEffect(() => {
    // Filter teams based on search term
    if (searchTerm.trim() === '') {
      setFilteredTeams(teams);
    } else {
      const term = searchTerm.toLowerCase();
      const filtered = teams.filter(team =>
        team.team.toString().includes(term) ||
        team.team.toString().startsWith(term)
      );
      setFilteredTeams(filtered);
    }
    setPage(1); // Reset to first page when filtering
  }, [searchTerm, teams]);

  const handleSortChange = (metric: string) => {
    if (sortBy === metric) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(metric);
      setSortOrder('desc');
    }
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(1);
  };

  const toggleTeamSelection = (teamNumber: number) => {
    setSelectedTeams(prev =>
      prev.includes(teamNumber)
        ? prev.filter(t => t !== teamNumber)
        : [...prev, teamNumber]
    );
  };

  const handleCompareTeams = async () => {
    if (selectedTeams.length < 2) {
      setError('Please select at least 2 teams to compare');
      return;
    }

    try {
      setComparisonLoading(true);
      setError(null);
      const result = await compareTeams(selectedTeams);
      setComparisonResults(result.data);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to compare teams';
      setError(errorMessage);
    } finally {
      setComparisonLoading(false);
    }
  };

  const paginatedTeams = filteredTeams.slice(
    (page - 1) * rowsPerPage,
    page * rowsPerPage
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Teams
      </Typography>

      {/* Search and Controls */}
      <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search teams by number..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.disabled' }} />
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Sort By</InputLabel>
              <Select
                value={sortBy}
                onChange={(e) => handleSortChange(e.target.value as string)}
                label="Sort By"
              >
                <MenuItem value="epa">EPA</MenuItem>
                <MenuItem value="opr">OPR</MenuItem>
                <MenuItem value="matches_played">Matches Played</MenuItem>
                <MenuItem value="copr_totalPoints">Total Points</MenuItem>
                <MenuItem value="copr_autoPoints">Auto Points</MenuItem>
                <MenuItem value="copr_teleopPoints">Teleop Points</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              onClick={handleCompareTeams}
              disabled={selectedTeams.length < 2 || comparisonLoading}
              startIcon={comparisonLoading ? <CircularProgress size={20} /> : null}
            >
              {comparisonLoading ? 'Comparing...' : `Compare (${selectedTeams.length})`}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Team Comparison Results */}
      {comparisonResults && (
        <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Team Comparison
          </Typography>
          <Grid container spacing={2}>
            {comparisonResults.map((team: any) => (
              <Grid item xs={12} md={6} lg={3} key={team.team}>
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" component="div">
                      Team {team.team}
                    </Typography>
                    <Divider sx={{ my: 1 }} />
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Typography variant="body2">
                        <strong>EPA:</strong> {team.epa.toFixed(2)}
                      </Typography>
                      <Typography variant="body2">
                        <strong>OPR:</strong> {team.opr.toFixed(2)}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Matches:</strong> {team.matches_played}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Total Points:</strong> {team.copr_totalPoints.toFixed(1)}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Teams Table */}
      <TableContainer component={Paper} elevation={3}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox"></TableCell>
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
                     onClick={() => handleSortChange('team')}
                >
                  Team <SortIcon sx={{ ml: 0.5, fontSize: 'small' }} />
                </Box>
              </TableCell>
              <TableCell align="right">
                <Box sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
                     onClick={() => handleSortChange('matches_played')}
                >
                  Matches <SortIcon sx={{ ml: 0.5, fontSize: 'small' }} />
                </Box>
              </TableCell>
              <TableCell align="right">
                <Box sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
                     onClick={() => handleSortChange('epa')}
                >
                  EPA <SortIcon sx={{ ml: 0.5, fontSize: 'small' }} />
                </Box>
              </TableCell>
              <TableCell align="right">
                <Box sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
                     onClick={() => handleSortChange('opr')}
                >
                  OPR <SortIcon sx={{ ml: 0.5, fontSize: 'small' }} />
                </Box>
              </TableCell>
              <TableCell align="right">Total Points</TableCell>
              <TableCell align="right">Auto Points</TableCell>
              <TableCell align="right">Teleop Points</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedTeams.map((team) => (
              <TableRow
                key={team.team}
                hover
                onClick={() => toggleTeamSelection(team.team)}
                selected={selectedTeams.includes(team.team)}
                sx={{ cursor: 'pointer' }}
              >
                <TableCell padding="checkbox">
                  {selectedTeams.includes(team.team) && <Chip label="Selected" size="small" color="primary" />}
                </TableCell>
                <TableCell component="th" scope="row">
                  <strong>Team {team.team}</strong>
                </TableCell>
                <TableCell align="right">{team.matches_played}</TableCell>
                <TableCell align="right">{team.epa.toFixed(2)}</TableCell>
                <TableCell align="right">{team.opr.toFixed(2)}</TableCell>
                <TableCell align="right">{team.copr_totalPoints.toFixed(1)}</TableCell>
                <TableCell align="right">{team.copr_autoPoints.toFixed(1)}</TableCell>
                <TableCell align="right">{team.copr_teleopPoints.toFixed(1)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
        <Pagination
          count={Math.ceil(filteredTeams.length / rowsPerPage)}
          page={page}
          onChange={handlePageChange}
          color="primary"
          showFirstButton
          showLastButton
        />
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1, mr: 2 }}>
        <TextField
          select
          label="Rows per page"
          value={rowsPerPage}
          onChange={handleRowsPerPageChange}
          size="small"
          sx={{ width: 120 }}
        >
          <MenuItem value={10}>10</MenuItem>
          <MenuItem value={25}>25</MenuItem>
          <MenuItem value={50}>50</MenuItem>
          <MenuItem value={100}>100</MenuItem>
        </TextField>
      </Box>
    </Box>
  );
};

export default TeamsPage;